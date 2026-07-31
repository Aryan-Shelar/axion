"use client";

import { Activity, Command, LayoutDashboard, Map, Search, UserRound } from "lucide-react";
import type { HermesGatewayStatus } from "@/lib/hermes/types";

export type DashboardView = "map" | "activity" | "dashboard";

const gatewayLabels: Record<HermesGatewayStatus, string> = { checking: "Checking Hermes", online: "Hermes Online", degraded: "Hermes Degraded", offline: "Hermes Offline", authentication: "Authentication Error" };

export function TopNavigation({ view, onViewChange, query, onQueryChange, gatewayStatus }: { view: DashboardView; onViewChange: (view: DashboardView) => void; query: string; onQueryChange: (query: string) => void; gatewayStatus: HermesGatewayStatus }) {
  const views = [
    { id: "map" as const, label: "Map", icon: Map },
    { id: "activity" as const, label: "Activity", icon: Activity },
    { id: "dashboard" as const, label: "Dashboard", icon: LayoutDashboard },
  ];
  return (
    <header className="top-nav">
      <div className="brand"><span className="brand-mark"><Command size={18} /></span><span>AXION</span><small>SKILLTREE</small><em>Prototype</em></div>
      <label className="search-box"><Search size={16} /><span className="sr-only">Search skills</span><input value={query} onChange={(event) => onQueryChange(event.target.value)} placeholder="Search skills or departments" /><kbd>⌘ K</kbd></label>
      <nav aria-label="Dashboard views">
        {views.map(({ id, label, icon: Icon }) => <button key={id} className={view === id ? "nav-tab active" : "nav-tab"} onClick={() => onViewChange(id)} aria-pressed={view === id}><Icon size={15} />{label}</button>)}
      </nav>
      <div className={`gateway gateway-${gatewayStatus}`} role="status"><span />{gatewayLabels[gatewayStatus]}</div>
      <button className="avatar" aria-label="Open user menu"><UserRound size={17} /></button>
    </header>
  );
}
