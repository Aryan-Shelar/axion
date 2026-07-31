import { Activity, BrainCircuit, CircleGauge, Clock3, Database, RefreshCw, Wrench } from "lucide-react";
import type { HermesDashboardOverview, HermesPublicError } from "@/lib/hermes/types";

type Props = { loading: boolean; data: HermesDashboardOverview | null; error: HermesPublicError | null; lastSuccessAt: string | null; onRefresh: () => void; readiness?: string };
const display = (value: string | number | null) => value ?? "Unavailable";

export function DashboardOverview({ loading, data, error, lastSuccessAt, onRefresh, readiness }: Props) {
  const active = data ? (data.activeRuns ?? 0) + (data.activeDelegations ?? 0) : null;
  const stats = data ? [
    { label: "Readiness", value: readiness ?? "Ready", icon: CircleGauge },
    { label: "Profile", value: display(data.profile), icon: BrainCircuit },
    { label: "Model", value: display(data.model), icon: Database },
    { label: "Installed skills", value: display(data.installedSkillsCount), icon: BrainCircuit },
    { label: "Available toolsets", value: display(data.toolsetsCount), icon: Wrench },
    { label: "Recent sessions", value: display(data.recentSessionsCount), icon: Clock3 },
    { label: "Active runs / delegations", value: display(active), icon: Activity },
  ] : [];
  return <main className="overview">
    <div className="overview-title hermes-overview-title"><div><span>HERMES / READ-ONLY BRIDGE</span><h1>Hermes overview</h1><p>Server-normalized operational metadata. Execution remains disabled in Phase A.</p></div><button onClick={onRefresh} aria-label="Refresh Hermes data"><RefreshCw size={15} />Refresh</button></div>
    {loading && !data ? <div className="hermes-panel-state">Loading Hermes overview…</div> : error && !data ? <div className="hermes-panel-state unavailable">{error.message}</div> : <>
      <div className="stat-grid hermes-stat-grid">{stats.map(({ label, value, icon: Icon }) => <article key={label}><Icon size={18} /><strong>{value}</strong><span>{label}</span></article>)}</div>
      <section className="department-overview refresh-summary"><header><div><Clock3 size={17} /><h2>Last successful refresh</h2></div><span>{lastSuccessAt ? new Date(lastSuccessAt).toLocaleString() : "Not yet available"}</span></header>{error && <div className="stale-note">Showing the last successful data while Hermes recovers.</div>}</section>
    </>}
  </main>;
}
