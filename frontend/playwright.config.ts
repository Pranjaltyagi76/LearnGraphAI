import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./tests",
  fullyParallel: true,
  forbidOnly: Boolean(process.env.CI),
  retries: 0,
  use: { baseURL: "http://127.0.0.1:3000", trace: "retain-on-failure" },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: [{
    command: "npm run start",
    url: "http://127.0.0.1:3000",
    reuseExistingServer: !process.env.CI,
  }, {
    command: "node scripts/start-test-api.mjs",
    url: "http://127.0.0.1:8000/health",
    reuseExistingServer: false,
  }],
});
