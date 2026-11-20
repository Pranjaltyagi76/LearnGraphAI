import { expect, test } from "@playwright/test";

async function enter(page: import("@playwright/test").Page) {
  await page.goto("/learn");
  await page.getByRole("button", { name: "Analyze this learner" }).click();
  await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
}
async function answer(page: import("@playwright/test").Page, option: string) {
  await page.locator(`input[type=radio][value=${option}]`).check();
  const checked = page.waitForResponse((r) => r.url().endsWith("/api/v1/demo/analyze"));
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await checked;
  await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
}

test("guided practice reaches a distinct reassessment and honestly remains developing", async ({ page, browser }) => {
  await enter(page);
  await expect(page.getByText("0 / 3", { exact: true })).toBeVisible();
  await answer(page, "c");
  await expect(page.getByText("1 accepted local events", { exact: false })).toBeVisible();
  await answer(page, "d");
  await expect(page.getByRole("heading", { name: "reassessment", exact: true })).toBeVisible();
  await answer(page, "c");
  await expect(page.getByText("Distinct reassessment received.", { exact: true })).toBeVisible();
  await expect(page.getByText("50.0%", { exact: true })).toBeVisible();
  await expect(page.getByText("supported estimate · developing", { exact: true })).toBeVisible();
  await expect(page.getByText("practice · catalog exhausted", { exact: true })).toBeVisible();
  await page.reload();
  await expect(page.getByText("Saved analysis · recheck before continuing", { exact: true })).toBeVisible();
  await expect(page.getByText("3 accepted local events", { exact: false })).toBeVisible();
  const isolated = await browser.newContext();
  const other = await isolated.newPage(); await other.goto("http://127.0.0.1:3000/learn");
  await expect(other.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await isolated.close();
  await page.getByRole("button", { name: "Reset local progress", exact: true }).click();
  await page.getByRole("button", { name: "Confirm reset", exact: true }).click();
  await expect(page.getByRole("button", { name: "Analyze this learner" })).toBeVisible();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
});

test("refresh restores the exact pending response and retry acknowledges it once", async ({ page }) => {
  await enter(page);
  let saved: unknown;
  await page.route("**/api/v1/demo/analyze", async (route) => {
    saved = route.request().postDataJSON(); await route.abort("failed");
  });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByRole("heading", { name: "Response pending — not accepted" })).toBeVisible();
  await page.reload();
  await expect(page.getByRole("heading", { name: "Response pending — not accepted" })).toBeVisible();
  await page.unroute("**/api/v1/demo/analyze");
  let retried: unknown;
  await page.route("**/api/v1/demo/analyze", async (route) => { retried = route.request().postDataJSON(); await route.continue(); });
  await page.getByRole("button", { name: "Retry pending response", exact: true }).click();
  await expect(page.getByText("1 accepted local events", { exact: false })).toBeVisible();
  expect(retried).toEqual(saved);
  await expect(page.getByRole("heading", { name: "Response pending — not accepted" })).toHaveCount(0);
});

test("reset during an in-flight response prevents stale acknowledgement", async ({ page }) => {
  await enter(page);
  let release: (() => void) | undefined;
  let arrived: (() => void) | undefined;
  const intercepted = new Promise<void>((resolve) => { arrived = resolve; });
  await page.route("**/api/v1/demo/analyze", async (route) => {
    const response = await route.fetch();
    arrived!(); await new Promise<void>((resolve) => { release = resolve; });
    await route.fulfill({ response }).catch(() => {});
  });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await intercepted;
  await page.getByRole("button", { name: "Reset local progress", exact: true }).click();
  await page.getByRole("button", { name: "Confirm reset", exact: true }).click();
  release!();
  await expect(page.getByRole("button", { name: "Analyze this learner" })).toBeVisible();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await expect(page.getByText("Correct response", { exact: true })).toHaveCount(0);
});

test("429 preserves pending input and exposes only a manual retry", async ({ page }) => {
  await enter(page);
  let count = 0;
  await page.route("**/api/v1/demo/analyze", (route) => {
    count++;
    return route.fulfill({ status: 429, headers: { "Retry-After": "1" }, json: {
      code: "quota_exhausted", message: "Synthetic limit", request_id: "45db2dd4-73e8-5c97-8cc5-59ed346c941e", details: [],
    } });
  });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "free demo request limit" })).toContainText("pending response is preserved");
  await expect(page.getByRole("button", { name: "Retry pending response", exact: true })).toBeDisabled();
  await expect(page.getByRole("button", { name: "Retry pending response", exact: true })).toBeEnabled();
  expect(count).toBe(1);
});

test("storage denied requires explicit session-only choice", async ({ page }) => {
  await page.addInitScript(() => { Object.defineProperty(window, "indexedDB", { get() { throw new Error("denied"); } }); });
  await page.goto("/learn");
  await expect(page.getByRole("button", { name: "Continue in this tab only" })).toBeVisible();
  await page.getByRole("button", { name: "Continue in this tab only" }).click();
  await expect(page.getByText("Session-only · no refresh recovery", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: "Analyze this learner" }).click();
  await expect(page.getByText("Live analysis · server-graded", { exact: true })).toBeVisible();
});

test("lesson read adds no evidence and four profiles remain isolated", async ({ page }) => {
  await enter(page);
  await page.getByRole("button", { name: /lesson base cases Available.*lesson support/ }).click();
  await page.getByRole("button", { name: "Mark lesson read", exact: true }).click();
  await expect(page.getByText("Lesson recorded · zero new observations", { exact: true })).toBeVisible();
  await expect(page.getByText("0 / 3", { exact: true })).toBeVisible();
  await page.getByRole("button", { name: /Leena sparse/ }).click();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await page.getByRole("button", { name: "Analyze this learner" }).click();
  await expect(page.getByRole("heading", { name: "no failed trigger", exact: true })).toBeVisible();
});

test("guided mobile UI fits and retains a usable form", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 }); await enter(page);
  expect(await page.evaluate(() => document.documentElement.scrollWidth > innerWidth)).toBe(false);
  await expect(page.getByRole("button", { name: "Submit response", exact: true })).toBeVisible();
});

test("failed storage commit prevents a network submission", async ({ page }) => {
  await enter(page);
  await page.evaluate(() => {
    IDBObjectStore.prototype.put = function () { throw new DOMException("denied", "QuotaExceededError"); };
  });
  let posts = 0;
  await page.route("**/api/v1/demo/analyze", (route) => { posts++; return route.continue(); });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByRole("button", { name: "Continue in this tab only" })).toBeVisible();
  expect(posts).toBe(0);
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
});

test("a profile switch ignores a previous profile's delayed response", async ({ page }) => {
  await enter(page);
  let release: (() => void) | undefined;
  let arrived: (() => void) | undefined;
  const intercepted = new Promise<void>((resolve) => { arrived = resolve; });
  await page.route("**/api/v1/demo/analyze", async (route) => {
    const response = await route.fetch(); arrived!();
    await new Promise<void>((resolve) => { release = resolve; });
    await route.fulfill({ response }).catch(() => {});
  });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click(); await intercepted;
  await page.getByRole("button", { name: /Leena sparse/ }).click(); release!();
  await expect(page.getByText("Leena's sandbox", { exact: true })).toBeVisible();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
  await expect(page.getByText("Correct response", { exact: true })).toHaveCount(0);
});

test("mismatched response digest is never acknowledged", async ({ page }) => {
  await enter(page);
  await page.route("**/api/v1/demo/analyze", async (route) => {
    const response = await route.fetch(); const body = await response.json();
    body.history_digest = "0".repeat(64); await route.fulfill({ json: body });
  });
  await page.locator("input[type=radio][value=c]").check();
  await page.getByRole("button", { name: "Submit response", exact: true }).click();
  await expect(page.getByRole("alert").filter({ hasText: "did not match" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "Response pending — not accepted" })).toBeVisible();
  await expect(page.getByText("0 accepted local events", { exact: false })).toBeVisible();
});
