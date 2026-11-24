import { HttpException } from "@nestjs/common";
import { FundApiClient } from "./fund-api.client";
import { PortalService } from "./portal.service";

const json = (body: unknown, status = 200) =>
  Promise.resolve(new Response(JSON.stringify(body), { status, headers: { "Content-Type": "application/json" } }));

function fakeFetch(routes: Record<string, () => Promise<Response>>) {
  const calls: string[] = [];
  const fn = ((url: string, init?: RequestInit) => {
    calls.push(`${init?.method ?? "GET"} ${url}`);
    const key = Object.keys(routes).find((k) => url.includes(k));
    return key ? routes[key]() : json({}, 404);
  }) as unknown as typeof fetch;
  return { fn, calls };
}

const ROUTES = {
  "/nav/2026-11-23": () => json({ fundId: "FL-0001", asOf: "2026-11-23", netAssets: 1737900.75, navPerShare: 13.9032 }),
  "/performance": () =>
    json({ fundId: "FL-0001", from: "2026-11-20", to: "2026-11-23", periodReturn: 0.004015,
      contributions: { FR0000120271: 0.010954, FR0000131104: -0.00825, US0378331005: 0.001315 } }),
  "/documents": () => json([{ id: "1", type: "PROSPECTUS", title: "Prospectus", language: "fr", publishedOn: "2026-01-15" }]),
};

describe("PortalService", () => {
  it("agrège VL, performance et documents de fund-api", async () => {
    const { fn, calls } = fakeFetch(ROUTES);
    const summary = await new PortalService(new FundApiClient("http://api", fn)).summary("FL-0001", "2026-11-20", "2026-11-23");

    expect(summary.navPerShare).toBe(13.9032);
    expect(summary.performance.periodReturnPct).toBe(0.4);
    expect(summary.topContributors.map((c) => c.isin)).toEqual(["FR0000120271", "FR0000131104", "US0378331005"]);
    expect(summary.topContributors[1].contributionPct).toBe(-0.83);
    expect(summary.documents).toEqual([{ title: "Prospectus", type: "PROSPECTUS", publishedOn: "2026-01-15" }]);
    expect(calls).toContain("POST http://api/api/funds/FL-0001/nav/2026-11-23");
  });

  it("propage un 404 de fund-api", async () => {
    const { fn } = fakeFetch({ ...ROUTES, "/nav/2026-11-23": () => json({}, 404) });
    await expect(new PortalService(new FundApiClient("http://api", fn)).summary("FL-0001", "2026-11-20", "2026-11-23"))
      .rejects.toMatchObject({ status: 404 });
  });

  it("transforme une erreur 500 en 502", async () => {
    const { fn } = fakeFetch({ ...ROUTES, "/documents": () => json({}, 500) });
    await expect(new FundApiClient("http://api", fn).documents("FL-0001")).rejects.toMatchObject({ status: 502 });
  });

  it("répond 502 si fund-api est injoignable", async () => {
    const fn = (() => Promise.reject(new Error("ECONNREFUSED"))) as unknown as typeof fetch;
    await expect(new FundApiClient("http://api", fn).documents("FL-0001")).rejects.toBeInstanceOf(HttpException);
  });
});
