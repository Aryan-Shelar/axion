"use client";

import { useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ActivityPanel } from "@/components/activity-panel";
import { DashboardOverview } from "@/components/dashboard-overview";
import { SkillDetailDrawer } from "@/components/skill-detail-drawer";
import { SkillTreeCanvas } from "@/components/skill-tree-canvas";
import { TopNavigation, type DashboardView } from "@/components/top-navigation";
import { activityEvents } from "@/data/activity";
import { skillById } from "@/data/skills";
import { useHermesDashboard } from "@/hooks/use-hermes-dashboard";
import { getAxionSkillInstallation } from "@/lib/hermes/skill-aliases";

export default function Home() {
  const [view, setView] = useState<DashboardView>("map");
  const [query, setQuery] = useState("");
  const [selectedSkillId, setSelectedSkillId] = useState<string | null>(null);
  const hermes = useHermesDashboard();
  const selectedSkill = useMemo(() => selectedSkillId ? skillById[selectedSkillId] : null, [selectedSkillId]);
  const installedHermesIds = useMemo(() => new Set((hermes.skills.data ?? []).map((skill) => skill.id)), [hermes.skills.data]);
  const installationAvailable = hermes.skills.data !== null;
  const selectedInstallation = selectedSkill ? getAxionSkillInstallation(selectedSkill.id, installedHermesIds, installationAvailable) : "unavailable";

  return <div className="app-shell">
    <TopNavigation view={view} onViewChange={setView} query={query} onQueryChange={setQuery} gatewayStatus={hermes.gatewayStatus} />
    <AnimatePresence mode="wait">
      {view === "map" && <motion.main className="map-view" key="map" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        <SkillTreeCanvas query={query} onSelectSkill={setSelectedSkillId} installedHermesIds={installedHermesIds} installationAvailable={installationAvailable} />
        <ActivityPanel events={activityEvents.slice(0, 3)} />
      </motion.main>}
      {view === "activity" && <motion.main className="activity-view" key="activity" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
        <div className="view-heading"><span>EVENT STREAM / LIVE</span><h1>System activity</h1><p>Every signal, decision, and output across the AXION network.</p></div><ActivityPanel events={activityEvents} expanded />
      </motion.main>}
      {view === "dashboard" && <motion.div key="dashboard" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
        <DashboardOverview loading={hermes.overview.loading} data={hermes.overview.data} error={hermes.overview.error} lastSuccessAt={hermes.overview.lastSuccessAt} onRefresh={() => { void hermes.refreshAll(); }} readiness={hermes.health.data?.readiness === "ready" ? "Ready" : hermes.health.data?.readiness === "degraded" ? "Degraded" : undefined} />
      </motion.div>}
    </AnimatePresence>
    <SkillDetailDrawer skill={selectedSkill} installation={selectedInstallation} onClose={() => setSelectedSkillId(null)} />
  </div>;
}
