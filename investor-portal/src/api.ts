export interface FundSummary {
  fundId: string;
  asOf: string;
  navPerShare: number;
  netAssets: number;
  performance: { from: string; to: string; periodReturnPct: number };
  topContributors: Array<{ isin: string; contributionPct: number }>;
  documents: Array<{ title: string; type: string; publishedOn: string }>;
}

export async function fetchSummary(fundId: string, from: string, to: string, fetchFn: typeof fetch = fetch): Promise<FundSummary> {
  const response = await fetchFn(`/portal/funds/${encodeURIComponent(fundId)}/summary?from=${from}&to=${to}`);
  if (!response.ok) {
    throw new Error(response.status === 404 ? "Aucune donnée pour ce fonds à ces dates." : `Erreur ${response.status}`);
  }
  return response.json();
}
