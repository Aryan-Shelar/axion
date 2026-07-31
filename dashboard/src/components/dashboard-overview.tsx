import { Activity, BrainCircuit, CheckCircle2, CircleGauge, Network } from "lucide-react";
import { departments } from "@/data/departments";
import { skills } from "@/data/skills";

export function DashboardOverview() {
  const stats = [{ label: "Active skills", value: "31", icon: BrainCircuit }, { label: "Completed today", value: "84", icon: CheckCircle2 }, { label: "Success rate", value: "96.4%", icon: CircleGauge }, { label: "Events / hour", value: "128", icon: Activity }];
  return <main className="overview"><div className="overview-title"><span>CONTROL PLANE / OVERVIEW</span><h1>AXION operating intelligence</h1><p>A live readout across every connected department and specialist skill.</p></div><div className="stat-grid">{stats.map(({ label, value, icon: Icon }) => <article key={label}><Icon size={18} /><strong>{value}</strong><span>{label}</span></article>)}</div><section className="department-overview"><header><div><Network size={17} /><h2>Department health</h2></div><span>{skills.length} skills connected</span></header><div>{departments.map((department, index) => <article key={department.id}><span className="dept-signal" style={{ background: department.color }} /><div><strong>{department.name}</strong><p>{department.description}</p></div><div className="health"><b>{92 + (index % 7)}%</b><span>HEALTH</span></div></article>)}</div></section></main>;
}
