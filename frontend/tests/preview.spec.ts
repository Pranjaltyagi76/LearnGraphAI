import { readFileSync } from "node:fs";
import { resolve } from "node:path";
import { expect, test } from "@playwright/test";

test("recorded example is labeled and never claims a live submission", async ({
  page,
}) => {
  await page.goto("/");
  await expect(
    page.getByRole("heading", { name: /Find the concept/ }),
  ).toBeVisible();
  await expect(page.getByText("Prerecorded example · synthetic")).toBeVisible();
  await page.getByRole("button", { name: "View recorded feedback" }).click();
  await expect(
    page.getByText(/This example was not submitted to a live service/),
  ).toBeVisible();
});

test("unavailable API preserves an honest recorded state", async ({ page }) => {
  await page.route("**/ready", (route) =>
    route.fulfill({ status: 503, json: { code: "not_configured" } }),
  );
  await page.goto("/");
  await page.getByRole("button", { name: "Check live connection" }).click();
  await expect(
    page.getByRole("alert").filter({ hasText: "The live demo" }),
  ).toContainText("no response has been accepted");
  await expect(page.getByText("Prerecorded example · synthetic")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Check my response" }),
  ).toHaveCount(0);
});

test("mobile preview fits the viewport", async ({ page }) => {
  await page.setViewportSize({ width: 390, height: 844 });
  await page.goto("/");
  const overflow = await page.evaluate(
    () => document.documentElement.scrollWidth > innerWidth,
  );
  expect(overflow).toBe(false);
  await expect(
    page.getByRole("button", { name: "View recorded feedback" }),
  ).toBeVisible();
});

// Browser/API contract fixture only; live Supabase verification is a separate gate.
test("connected question selection and grading feedback follow the API contract", async ({
  page,
}) => {
  const fixture = JSON.parse(
    readFileSync(
      resolve(process.cwd(), "../backend/data/phase1.json"),
      "utf8",
    ),
  );
  await page.route("**/ready", (route) =>
    route.fulfill({ json: { status: "ready" } }),
  );
  await page.route("**/api/v1/demo/profiles", (route) =>
    route.fulfill({ json: { profiles: fixture.profiles } }),
  );
  await page.route("**/api/v1/demo/profiles/*/seed", (route) =>
    route.fulfill({
      json: {
        release_id: fixture.release_id,
        profile: fixture.profiles[0],
        seed_events: fixture.seed_events,
        activities: fixture.questions.map(
          ({
            correct_option,
            explanation,
            ...question
          }: {
            correct_option: string;
            explanation: string;
            id: string;
          }) => {
            void correct_option;
            void explanation;
            return question;
          },
        ),
      },
    }),
  );
  await page.route("**/api/v1/bootstrap/answer", (route) => {
    const body = route.request().postDataJSON();
    expect(body.activity_id).toBe("base_cases_practice_03");
    expect(body.option_id).toBe("c");
    expect(body).not.toHaveProperty("is_correct");
    return route.fulfill({
      json: { is_correct: true, explanation: "Boundary inputs return n." },
    });
  });
  await page.goto("/");
  await page.getByRole("button", { name: "Check live connection" }).click();
  await expect(page.getByText("Live question · server-graded")).toBeVisible();
  await page.getByRole("radio", { name: "C n", exact: true }).check();
  await page.getByRole("button", { name: "Check my response" }).click();
  await expect(page.getByText("Boundary inputs return n.")).toBeVisible();
  await expect(
    page.getByRole("button", { name: "Response checked" }),
  ).toBeDisabled();
});
