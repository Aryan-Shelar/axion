"use client";

import { Activity, Command, LayoutDashboard, Map, Search, UserRound } from "lucide-react";

export type DashboardView = "map" | "activity" | "dashboard";

export function TopNavigation({ view, onViewChange, query, onQueryChange }: { view: DashboardView; onViewChange: (view: DashboardView) => void; query: string; onQueryChange: (query: string) => void }) {
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
      <div className="gateway"><span />Gateway demo</div>
      <button className="avatar" aria-label="Open user menu"><UserRound size={17} /></button>
    </header>
  );
}
