import { useState } from "react";
import { FundSummaryView } from "./FundSummaryView";

export function App() {
  const [fundId, setFundId] = useState("FL-0001");
  const [from, setFrom] = useState("2026-11-20");
  const [to, setTo] = useState("2026-11-23");

  return (
    <main>
      <h1>Portail investisseurs FundLens</h1>
      <form onSubmit={(e) => e.preventDefault()} className="filters">
        <label>Fonds <input value={fundId} onChange={(e) => setFundId(e.target.value)} /></label>
        <label>Du <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} /></label>
        <label>Au <input type="date" value={to} onChange={(e) => setTo(e.target.value)} /></label>
      </form>
      <FundSummaryView fundId={fundId} from={from} to={to} />
    </main>
  );
}
