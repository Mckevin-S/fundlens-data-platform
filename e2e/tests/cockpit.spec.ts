import { expect, test } from "@playwright/test";

test.beforeEach(async ({ page }) => {
  if (process.env.E2E_FULL_STACK === "1") return;
  await page.route("**/api/funds/FL-0001/nav/**", (r) =>
    r.fulfill({ json: { fundId: "FL-0001", asOf: "2026-11-23", netAssets: 1737900.75, navPerShare: 13.9032 } }));
  await page.route("**/api/funds/FL-0001/performance**", (r) =>
    r.fulfill({ json: { fundId: "FL-0001", from: "2026-11-20", to: "2026-11-23", periodReturn: 0.004015,
      contributions: { FR0000120271: 0.010954, FR0000131104: -0.00825, US0378331005: 0.001315 } } }));
  await page.route("**/api/funds/FL-0001/alerts", (r) => r.fulfill({ json: [] }));
});

test("le gérant calcule la VL et voit les contributions", async ({ page }) => {
  await page.goto("/");
  await page.getByRole("button", { name: "Calculer" }).click();
  await expect(page.getByTestId("nav")).toHaveText(/13,9032/);
  await expect(page.getByTestId("perf")).toHaveText(/0,40/);
  await expect(page.locator(".bars li")).toHaveCount(3);
  await expect(page.locator(".bars li").first()).toContainText("FR0000120271");
  await expect(page.getByText("Aucune alerte.")).toBeVisible();
});
