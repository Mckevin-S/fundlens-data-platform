import { useEffect, useState } from "react";
import { fetchSummary, type FundSummary } from "./api";
import { formatDate, formatEur, formatNav, formatPct } from "./format";

interface Props {
  fundId: string;
  from: string;
  to: string;
  load?: typeof fetchSummary;
}

export function FundSummaryView({ fundId, from, to, load = fetchSummary }: Props) {
  const [summary, setSummary] = useState<FundSummary | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setSummary(null);
    setError(null);
    load(fundId, from, to)
      .then((s) => !cancelled && setSummary(s))
      .catch((e: Error) => !cancelled && setError(e.message));
    return () => {
      cancelled = true;
    };
  }, [fundId, from, to, load]);

  if (error) return <p role="alert" className="error">{error}</p>;
  if (!summary) return <p aria-busy="true">Chargement…</p>;

  const perf = summary.performance.periodReturnPct;
  return (
    <section aria-label={`Fonds ${summary.fundId}`}>
      <h2>Fonds {summary.fundId}</h2>
      <dl className="kpis">
        <div><dt>Valeur liquidative au {formatDate(summary.asOf)}</dt><dd>{formatNav(summary.navPerShare)}</dd></div>
        <div><dt>Actif net</dt><dd>{formatEur(summary.netAssets)}</dd></div>
        <div>
          <dt>Performance du {formatDate(summary.performance.from)} au {formatDate(summary.performance.to)}</dt>
          <dd className={perf >= 0 ? "up" : "down"}>{formatPct(perf)}</dd>
        </div>
      </dl>
      <h3>Principales contributions</h3>
      <table>
        <thead><tr><th>ISIN</th><th>Contribution</th></tr></thead>
        <tbody>
          {summary.topContributors.map((c) => (
            <tr key={c.isin}><td>{c.isin}</td><td>{formatPct(c.contributionPct)}</td></tr>
          ))}
        </tbody>
      </table>
      <h3>Documents</h3>
      {summary.documents.length === 0 ? (
        <p>Aucun document publié.</p>
      ) : (
        <ul>{summary.documents.map((d) => <li key={d.title}>{d.title} ({d.type}, {formatDate(d.publishedOn)})</li>)}</ul>
      )}
    </section>
  );
}
