import { Injectable } from "@nestjs/common";
import { FundApiClient } from "./fund-api.client";

export interface FundSummary {
  fundId: string;
  asOf: string;
  navPerShare: number;
  netAssets: number;
  performance: { from: string; to: string; periodReturnPct: number };
  topContributors: Array<{ isin: string; contributionPct: number }>;
  documents: Array<{ title: string; type: string; publishedOn: string }>;
}

/** Pourcentage à 2 décimales, arrondi symétrique (−0,825 % → −0,83 %). */
const pct = (x: number) => (Math.sign(x) * Math.round(Math.abs(x) * 10000)) / 100;

/** Vue « investisseur » : une seule requête du front, plusieurs appels à fund-api en parallèle. */
@Injectable()
export class PortalService {
  constructor(private readonly api: FundApiClient) {}

  async summary(fundId: string, from: string, to: string): Promise<FundSummary> {
    const [nav, perf, documents] = await Promise.all([
      this.api.nav(fundId, to),
      this.api.performance(fundId, from, to),
      this.api.documents(fundId),
    ]);
    const topContributors = Object.entries(perf.contributions)
      .map(([isin, c]) => ({ isin, contributionPct: pct(c) }))
      .sort((a, b) => Math.abs(b.contributionPct) - Math.abs(a.contributionPct))
      .slice(0, 5);
    return {
      fundId,
      asOf: nav.asOf,
      navPerShare: nav.navPerShare,
      netAssets: nav.netAssets,
      performance: { from: perf.from, to: perf.to, periodReturnPct: pct(perf.periodReturn) },
      topContributors,
      documents: documents.map(({ title, type, publishedOn }) => ({ title, type, publishedOn })),
    };
  }
}
