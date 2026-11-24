import { expect, test } from "@playwright/test";

const SUMMARY = {
  fundId: "FL-0001", asOf: "2026-11-23", navPerShare: 13.9032, netAssets: 1737900.75,
  performance: { from: "2026-11-20", to: "2026-11-23", periodReturnPct: 0.4 },
  topContributors: [{ isin: "FR0000120271", contributionPct: 1.1 }, { isin: "FR0000131104", contributionPct: -0.83 }],
  documents: [{ title: "Prospectus FundLens Actions Europe", type: "PROSPECTUS", publishedOn: "2026-01-15" }],
};

test.beforeEach(async ({ page }) => {
  if (process.env.E2E_FULL_STACK === "1") return;
  await page.route("**/portal/funds/**", (route) =>
    route.request().url().includes("FL-0001")
      ? route.fulfill({ json: SUMMARY })
      : route.fulfill({ status: 404, json: {} }));
});

test("l'investisseur consulte la VL, la performance et les documents", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "Fonds FL-0001" })).toBeVisible();
  await expect(page.getByText("13,9032 €")).toBeVisible();
  await expect(page.getByText("+0,40 %")).toBeVisible();
  await expect(page.getByRole("cell", { name: "FR0000120271" })).toBeVisible();
  await expect(page.getByText(/Prospectus FundLens Actions Europe/)).toBeVisible();
});

test("un fonds inconnu affiche un message d'erreur", async ({ page }) => {
  await page.goto("/");
  await page.getByLabel("Fonds").fill("FL-9999");
  await expect(page.getByRole("alert")).toContainText("Aucune donnée");
});
