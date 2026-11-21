import { expect, test, type Page } from "@playwright/test";
import axe from "axe-core";
import { readFileSync } from "node:fs";
import { resolve } from "node:path";

const catalog = JSON.parse(readFileSync(resolve(process.cwd(), "../curriculum/catalog-full.v1.json"), "utf8")) as {
  activities: { id: string; correct_option?: string }[];
};

async function respond(page: Page, correct: boolean) {
  const id = await page.locator("input[type=radio]").first().getAttribute("name");
  const key = catalog.activities.find((a) => a.id === id)!.correct_option!;
  const option = correct ? key : ["a", "b", "c", "d"].find((o) => o !== key)!;
  await page.locator(`input[type=radio][value=${option}]`).check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
}

async function enter(page: Page, url = "/learn") {
  await page.goto(url);
  await page.getByRole("button", { name: "Analyze this learner", exact: true }).click();
  await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
}

test("full release presents four contrasting profiles with actual server states", async ({ page }) => {
  await enter(page);
  await expect(page.getByRole("list", { name: "Concept evidence and prerequisites" }).locator(":scope > li")).toHaveCount(12);
  await expect(page.getByRole("heading", { name: "A supported hypothesis" })).toBeVisible();
  for (const [name, status] of [["Arjun", "A supported hypothesis"], ["Leena", "no failed trigger"], ["Kabir", "ambiguous"]]) {
    await page.getByRole("button", { name: new RegExp(name) }).click();
    await page.getByRole("button", { name: "Analyze this learner", exact: true }).click();
    await expect(page.getByRole("heading", { name: status, exact: true })).toBeVisible();
    await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  }
});

test("keyboard concept selection requires a consistent reanalysis and offers the same list", async ({ page }) => {
  await enter(page);
  const focus = page.getByRole("button", { name: "Focus on memoization", exact: true });
  await focus.focus(); await page.keyboard.press("Enter");
  await expect(page.getByRole("status").filter({ hasText: "Focus changed to memoization" })).toBeVisible();
  await expect(page.getByRole("button", { name: "Submit response", exact: true })).toBeDisabled();
  await page.getByRole("button", { name: "Recheck live analysis", exact: true }).click();
  await expect(page.getByRole("status").filter({ hasText: "Focus changed" })).toHaveCount(0);
  await page.getByRole("button", { name: "List view", exact: true }).click();
  await expect(page.getByRole("button", { name: "Focus on memoization", exact: true })).toHaveAttribute("aria-pressed", "true");
  await expect(page.locator(".graph-scroll")).toHaveCount(0);
  await expect(page.getByText("Needs ready prerequisites:", { exact: false }).first()).toBeVisible();
});

test("diagnosis IDs link to the inspectable canonical timeline with provenance and hint policy", async ({ page }) => {
  await enter(page);
  await page.getByText("Inspect diagnosis evidence", { exact: true }).click();
  const evidence = page.locator(".gap-card a[href^='#event-']");
  await expect(evidence).toHaveCount(3);
  await evidence.first().click();
  const target = page.locator(`li${await evidence.first().getAttribute("href")}`);
  await target.getByText("Inspect this event", { exact: true }).click();
  await expect(target).toContainText("Synthetic seed");
  await expect(target).toContainText("Hints: 0");
  await page.getByLabel("Timeline evidence", { exact: true }).selectOption("visitor_demo");
  await expect(page.getByText("No events in this view.", { exact: false })).toBeVisible();
});

test("retained histories reopen separately from the full release without migration", async ({ page }) => {
  await enter(page, "/learn?release=learngraph-review-v1");
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByText("1 accepted local events", { exact: false })).toBeVisible();
  await page.goto("/learn");
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await page.goto("/learn?release=learngraph-review-v1");
  await expect(page.getByText("1 accepted local events", { exact: false })).toBeVisible();
  await expect(page.getByText("Saved analysis · recheck before continuing", { exact: true })).toBeVisible();
});

test("versioned read-only examples remain usable when every live API request fails", async ({ page }) => {
  await page.route("**/api/v1/**", (route) => route.abort("failed"));
  await page.goto("/learn");
  await page.getByRole("link", { name: "Open the versioned, read-only examples →" }).click();
  await page.getByRole("link", { name: "Inspect Arjun's example →" }).click();
  await expect(page.getByText("No live submission in this example.", { exact: true })).toBeVisible();
  await page.getByText("Recorded versions & hash", { exact: true }).click();
  await expect(page.getByText("learngraph-full-v1", { exact: false })).toBeVisible();
  await expect(page.getByRole("heading", { name: "A supported hypothesis" })).toBeVisible();
  await expect(page.locator("form, input[type=radio]")).toHaveCount(0);
});

test("early failed evidence abstains and supported ready evidence yields no supported gap", async ({ page }) => {
  await enter(page, "/learn?profile=demo_sparse");
  await expect(page.getByText("early estimate · early", { exact: true })).toBeVisible();
  await respond(page, false);
  await expect(page.getByRole("heading", { name: "insufficient evidence", exact: true })).toBeVisible();
  await page.getByRole("button", { name: /Kabir ambiguous/ }).click();
  await page.getByRole("button", { name: "Analyze this learner", exact: true }).click();
  await respond(page, true); await respond(page, true);
  await expect(page.getByRole("heading", { name: "no supported gap", exact: true })).toBeVisible();
});

test("a retained release without a suitable activity explains the empty plan", async ({ page }) => {
  await enter(page, "/learn?release=learngraph-review-v1");
  await page.getByRole("button", { name: "Focus on state definition", exact: true }).click();
  await page.getByRole("button", { name: "Recheck live analysis", exact: true }).click();
  await expect(page.getByRole("heading", { name: "no suitable activity", exact: true })).toBeVisible();
  await expect(page.getByText("No currently permitted fresh question is available.", { exact: false })).toBeVisible();
  await expect(page.getByRole("button", { name: "Submit response", exact: true })).toHaveCount(0);
});

for (const mobile of [false, true]) {
  test(`accessibility scan, keyboard controls and reduced motion (${mobile ? "mobile" : "desktop"})`, async ({ page }) => {
    await page.setViewportSize(mobile ? { width: 360, height: 800 } : { width: 1440, height: 1000 });
    await page.emulateMedia({ reducedMotion: "reduce" });
    for (const url of ["/learn", "/examples", "/examples/demo_upstream", "/methodology"]) {
      if (url === "/learn") await enter(page); else await page.goto(url);
      expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
      expect(await page.evaluate(() => getComputedStyle(document.documentElement).scrollBehavior)).toBe("auto");
      await page.addScriptTag({ content: axe.source });
      const violations = await page.evaluate(async () => (await (window as unknown as { axe: typeof axe }).axe.run(document, {
        runOnly: { type: "tag", values: ["wcag2a", "wcag2aa", "wcag21aa", "best-practice"] },
      })).violations.map((v) => ({ id: v.id, nodes: v.nodes.map((n) => n.target) })));
      expect(violations, url).toEqual([]);
    }
    await page.goto("/learn");
    await expect(page.getByRole("button", { name: /^(Analyze this learner|Recheck live analysis)$/ })).toBeVisible();
    await page.getByRole("button", { name: /^(Analyze this learner|Recheck live analysis)$/ }).focus();
    await page.keyboard.press("Enter");
    await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
    await page.locator("input[type=radio]").first().focus(); await page.keyboard.press("Space");
    await page.getByRole("button", { name: "Submit response", exact: true }).focus(); await page.keyboard.press("Enter");
    await expect(page.getByText("1 accepted local events", { exact: false })).toBeVisible();
  });
}
