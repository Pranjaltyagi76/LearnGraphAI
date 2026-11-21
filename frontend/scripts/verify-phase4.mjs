// Real public browser/API verification. No route mocks, credentials, or seed mutations.
import { chromium, expect } from "@playwright/test";
import { mkdir, writeFile } from "node:fs/promises";
import { dirname, resolve } from "node:path";
import { parseArgs } from "node:util";
import axe from "axe-core";

const { values } = parseArgs({ options: {
  output: { type: "string", default: "../context/evidence/phase4_live.json" },
  screenshot: { type: "string", default: "../context/evidence/phase4_live_desktop.png" },
} });
const base = "https://learngraph-ai-web.vercel.app";
const api = "https://learngraph-ai-api.vercel.app";
const report = { observed_at: new Date().toISOString(), frontend: base, api,
  method: "Fresh Chromium browser → public production API → canonical Supabase release; no mocks or automatic POST retries.",
  synthetic_only: true, checks: {}, requests: [], browser_errors: [] };
const first = await chromium.launch({ headless: true });
const second = await chromium.launch({ headless: true });
try {
  const context = await first.newContext({ viewport: { width: 1365, height: 1000 } });
  const page = await context.newPage();
  page.on("pageerror", (e) => report.browser_errors.push(e.message));
  async function get(path) {
    const started = performance.now();
    const response = await context.request.get(`${api}${path}`, { headers: { Origin: base }, timeout: 15000 });
    const body = await response.json();
    report.requests.push({ method: "GET", path, status: response.status(), elapsed_ms: Math.round(performance.now()-started),
      request_id: response.headers()["x-request-id"], server_timing: response.headers()["server-timing"] });
    expect(response.status()).toBe(200);
    expect(response.headers()["access-control-allow-origin"]).toBe(base);
    return body;
  }
  const health = await get("/health"); expect(health.stage).toBe("phase4");
  await get("/ready");
  const release = await get("/api/v1/demo/release");
  report.release = release;
  expect(release.release_id).toBe("learngraph-full-v1");
  const profiles = await get(`/api/v1/releases/${release.release_id}/profiles`);
  expect(profiles.profiles).toHaveLength(4);
  const seed = await get(`/api/v1/releases/${release.release_id}/profiles/demo_base_cases/seed`);
  expect(seed.activities.every((a) => !("correct_option" in a) && !("explanation" in a))).toBe(true);
  expect(seed.concepts).toHaveLength(12); expect(seed.activities).toHaveLength(84);
  for (const concept of seed.concepts) {
    const items = seed.activities.filter((a) => a.primary_concept_id === concept.id);
    expect(items.filter((a) => a.kind === "question")).toHaveLength(6);
    expect(items.filter((a) => a.kind === "lesson")).toHaveLength(1);
  }
  report.profiles = [];
  for (const p of profiles.profiles.filter((p) => p.id !== "demo_base_cases")) {
    const profile = await get(`/api/v1/releases/${release.release_id}/profiles/${p.id}/seed`);
    expect(profile.activities).toHaveLength(84);
    expect(profile.versions.release_hash).toBe(release.release_hash);
    report.profiles.push({ id: p.id, focus: profile.profile.focus_concept_id,
      seed_events: profile.seed_events.length, versions: profile.versions });
  }
  const retained = await get("/api/v1/releases/learngraph-review-v1/profiles/demo_base_cases/seed");
  expect(retained.activities).toHaveLength(14);
  expect(retained.versions.release_id).toBe("learngraph-review-v1");
  report.checks.retained_slice_readable = true;
  const measured = await context.request.get(`${api}/api/v1/analytics/evaluation`);
  expect(measured.status()).toBe(404);
  expect((await measured.json()).code).toBe("evaluation_not_published");
  report.checks.no_mislabelled_full_catalog_quality_summary = true;
  report.checks.metadata_versions_projection_cors = true;

  await page.goto(`${base}/learn`, { waitUntil: "networkidle" });
  await expect(page.getByRole("list", { name: "Concept evidence and prerequisites" }).locator(":scope > li")).toHaveCount(12);
  async function analyzed(action, expectedEvents) {
    const responsePromise = page.waitForResponse((r) => r.url() === `${api}/api/v1/demo/analyze` && r.request().method() === "POST");
    const started = performance.now();
    await action(); const response = await responsePromise; const bundle = await response.json();
    report.requests.push({ method: "POST", path: "/api/v1/demo/analyze", status: response.status(),
      elapsed_ms: Math.round(performance.now()-started), request_id: response.headers()["x-request-id"],
      accepted_visitor_events: bundle.accepted_visitor_events, history_digest: bundle.history_digest,
      diagnosis: bundle.diagnosis?.status, plan_status: bundle.plan?.status });
    expect(response.status()).toBe(200); expect(bundle.accepted_visitor_events).toBe(expectedEvents);
    expect(bundle.persisted).toBe(false); expect(bundle.versions.release_hash).toBe(release.release_hash);
    await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
    await expect(page.getByText(`${expectedEvents} accepted local events`, { exact: false })).toBeVisible();
    return bundle;
  }
  const before = await analyzed(() => page.getByRole("button", { name: "Analyze this learner" }).click(), 0);
  const actions = [
    ["base_cases_practice_03", "c"], ["base_cases_practice_04", "d"], ["base_cases_reassessment_01", "c"],
  ];
  let after = before;
  for (let i = 0; i < actions.length; i++) {
    const [id, option] = actions[i];
    expect(await page.locator("input[type=radio]").first().getAttribute("name")).toBe(id);
    await page.locator(`input[type=radio][value=${option}]`).check();
    after = await analyzed(() => page.getByRole("button", { name: "Submit response", exact: true }).click(), i+1);
  }
  const priorEstimate = before.estimates.find((e) => e.concept_id === "base_cases");
  const currentEstimate = after.estimates.find((e) => e.concept_id === "base_cases");
  expect(priorEstimate.eligible_count).toBe(3); expect(priorEstimate.successes).toBe(0);
  expect(currentEstimate.eligible_count).toBe(6); expect(currentEstimate.successes).toBe(3);
  expect(currentEstimate.estimate).toBe(.5); expect(currentEstimate.performance_state).toBe("developing");
  expect(after.plan.status).toBe("catalog_exhausted");
  await expect(page.getByText("Distinct reassessment received.", { exact: true })).toBeVisible();
  report.before = priorEstimate; report.after = currentEstimate;
  report.checks.real_practice_distinct_reassessment = true;
  await page.getByRole("button", { name: "List view", exact: true }).click();
  await expect(page.locator(".graph-scroll")).toHaveCount(0);
  await expect(page.getByRole("list", { name: "Concept evidence and prerequisites" }).locator(":scope > li")).toHaveCount(12);
  await page.getByRole("button", { name: "Graph view", exact: true }).click();
  await mkdir(dirname(resolve(values.screenshot)), { recursive: true });
  await page.screenshot({ path: resolve(values.screenshot), fullPage: true });
  await page.setViewportSize({ width: 390, height: 844 });
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  report.checks.mobile_overflow = false;
  const mobile = resolve(values.screenshot).replace(/\.png$/, "_mobile.png");
  await page.screenshot({ path: mobile, fullPage: true });
  await page.setViewportSize({ width: 1365, height: 1000 });
  await page.reload({ waitUntil: "networkidle" });
  await expect(page.getByText("Saved analysis · recheck before continuing", { exact: true })).toBeVisible();
  await expect(page.getByText("3 accepted local events", { exact: false })).toBeVisible();
  report.checks.refresh_restores_acknowledged_history = true;
  const other = await second.newPage({ viewport: { width: 1280, height: 900 } });
  await other.goto(`${base}/learn`, { waitUntil: "networkidle" });
  await expect(other.getByText("0 accepted local events", { exact: false })).toBeVisible();
  const otherResponse = other.waitForResponse((r) => r.url() === `${api}/api/v1/demo/analyze` && r.request().method() === "POST");
  await other.getByRole("button", { name: "Analyze this learner" }).click();
  const secondResult = await otherResponse; expect(secondResult.status()).toBe(200);
  const isolated = await secondResult.json();
  expect(isolated.accepted_visitor_events).toBe(0);
  expect(isolated.estimates.find((e) => e.concept_id === "base_cases").successes).toBe(0);
  expect(isolated.sandbox_id).not.toBe(after.sandbox_id);
  report.checks.two_independent_browsers = true;
  report.independent_browser = { status: secondResult.status(), visitor_events: isolated.accepted_visitor_events,
    history_digest: isolated.history_digest, distinct_sandbox: true };
  await page.getByRole("button", { name: "Reset local progress", exact: true }).click();
  await page.getByRole("button", { name: "Confirm reset", exact: true }).click();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Analyze this learner" })).toBeVisible();
  report.checks.reset_is_local = true;
  report.accessibility = [];
  await page.emulateMedia({ reducedMotion: "reduce" });
  for (const mobile of [false, true]) {
    await page.setViewportSize(mobile ? { width: 360, height: 800 } : { width: 1365, height: 1000 });
    for (const path of ["/learn", "/examples", "/examples/demo_upstream", "/methodology"]) {
      await page.goto(`${base}${path}`, { waitUntil: "networkidle" });
      if (path === "/learn") await expect(page.getByRole("button", { name: "Analyze this learner", exact: true })).toBeVisible();
      if (path === "/examples/demo_upstream") {
        await expect(page.getByText("No live submission in this example.", { exact: true })).toBeVisible();
        await expect(page.locator("form, input[type=radio]")).toHaveCount(0);
      }
      await page.addScriptTag({ content: axe.source });
      const scan = await page.evaluate(async () => {
        const result = await window.axe.run(document, { runOnly: {
          type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa", "best-practice"],
        } });
        return { violations: result.violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })),
          incomplete_rules: result.incomplete.map((v) => v.id),
          horizontal_overflow: document.documentElement.scrollWidth > innerWidth,
          reduced_motion_scroll: getComputedStyle(document.documentElement).scrollBehavior };
      });
      expect(scan.violations).toEqual([]); expect(scan.horizontal_overflow).toBe(false);
      expect(scan.reduced_motion_scroll).toBe("auto");
      report.accessibility.push({ path, mobile, axe_version: axe.version, ...scan });
    }
  }
  report.checks.graph_list_and_readonly_examples = true;
  report.checks.no_browser_exceptions = report.browser_errors.length === 0;
  expect(report.browser_errors).toEqual([]);
  report.passed = true;
} catch (error) {
  report.passed = false; report.failure = error instanceof Error ? error.message : String(error);
} finally {
  await first.close(); await second.close();
  await mkdir(dirname(resolve(values.output)), { recursive: true });
  await writeFile(resolve(values.output), JSON.stringify(report, null, 2) + "\n", { flag: "wx" });
}
console.log(JSON.stringify({ passed: report.passed, output: values.output, requests: report.requests.length }));
if (!report.passed) process.exitCode = 1;
