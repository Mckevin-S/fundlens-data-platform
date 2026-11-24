const eur = new Intl.NumberFormat("fr-FR", { style: "currency", currency: "EUR" });
const nav = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 4, maximumFractionDigits: 4 });
const pct = new Intl.NumberFormat("fr-FR", { minimumFractionDigits: 2, maximumFractionDigits: 2, signDisplay: "exceptZero" });

export const formatEur = (x: number) => eur.format(x);
export const formatNav = (x: number) => `${nav.format(x)} €`;
export const formatPct = (x: number) => `${pct.format(x)} %`;
export const formatDate = (iso: string) => new Date(`${iso}T00:00:00`).toLocaleDateString("fr-FR");
