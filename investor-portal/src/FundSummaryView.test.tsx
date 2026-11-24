import { render, screen } from "@testing-library/react";
import { FundSummaryView } from "./FundSummaryView";
import { fetchSummary, type FundSummary } from "./api";

const SUMMARY: FundSummary = {
  fundId: "FL-0001",
  asOf: "2026-11-23",
  navPerShare: 13.9032,
  netAssets: 1737900.75,
  performance: { from: "2026-11-20", to: "2026-11-23", periodReturnPct: 0.4 },
  topContributors: [{ isin: "FR0000120271", contributionPct: 1.1 }, { isin: "FR0000131104", contributionPct: -0.83 }],
  documents: [{ title: "Prospectus", type: "PROSPECTUS", publishedOn: "2026-01-15" }],
};

describe("FundSummaryView", () => {
  it("affiche VL, performance, contributions et documents", async () => {
    render(<FundSummaryView fundId="FL-0001" from="2026-11-20" to="2026-11-23" load={() => Promise.resolve(SUMMARY)} />);

    expect(await screen.findByRole("heading", { name: "Fonds FL-0001" })).toBeInTheDocument();
    expect(screen.getByText(/13,9032/)).toBeInTheDocument();
    expect(screen.getByText("+0,40 %")).toHaveClass("up");
    expect(screen.getByText(/^[-−]0,83 %$/)).toBeInTheDocument();
    expect(screen.getByText(/Prospectus \(PROSPECTUS, 15\/01\/2026\)/)).toBeInTheDocument();
  });

  it("affiche l'erreur renvoyée par le BFF", async () => {
    render(<FundSummaryView fundId="FL-9999" from="2026-11-20" to="2026-11-23" load={() => Promise.reject(new Error("Aucune donnée"))} />);
    expect(await screen.findByRole("alert")).toHaveTextContent("Aucune donnée");
  });
});

describe("fetchSummary", () => {
  it("appelle le BFF et traduit un 404", async () => {
    const calls: string[] = [];
    const notFound = ((url: string) => {
      calls.push(url);
      return Promise.resolve(new Response("{}", { status: 404 }));
    }) as unknown as typeof fetch;

    await expect(fetchSummary("FL-0001", "2026-11-20", "2026-11-23", notFound)).rejects.toThrow("Aucune donnée");
    expect(calls).toEqual(["/portal/funds/FL-0001/summary?from=2026-11-20&to=2026-11-23"]);
  });

  it("renvoie le JSON en cas de succès", async () => {
    const ok = (() => Promise.resolve(new Response(JSON.stringify(SUMMARY)))) as unknown as typeof fetch;
    await expect(fetchSummary("FL-0001", "a", "b", ok)).resolves.toEqual(SUMMARY);
  });
});
