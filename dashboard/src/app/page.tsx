"use client";

import { useCallback, useMemo, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { ActivityPanel } from "@/components/activity-panel";
import { DashboardOverview } from "@/components/dashboard-overview";
import { SkillDetailDrawer } from "@/components/skill-detail-drawer";
import { SessionDetailDrawer } from "@/components/session-detail-drawer";
import { RunProgressDrawer } from "@/components/run-progress-drawer";
import { RunSkillDialog } from "@/components/run-skill-dialog";
import { SkillTreeCanvas } from "@/components/skill-tree-canvas";
import { TopNavigation, type DashboardView } from "@/components/top-navigation";
import { skillById } from "@/data/skills";
import { useHermesDashboard } from "@/hooks/use-hermes-dashboard";
import { useHermesRun } from "@/hooks/use-hermes-run";
import { getAxionSkillInstallation } from "@/lib/hermes/skill-aliases";
import type { HermesSessionSummary } from "@/lib/hermes/types";

export default function Home() {
  const [view, setView] = useState<DashboardView>("map");
  const [query, setQuery] = useState("");
  const [selectedSkillId, setSelectedSkillId] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<HermesSessionSummary | null>(null);
  const [sessionOpener, setSessionOpener] = useState<HTMLButtonElement | null>(null);
  const [runDialogOpen, setRunDialogOpen] = useState(false);
  const [runOpener, setRunOpener] = useState<HTMLButtonElement | null>(null);
  const hermes = useHermesDashboard();
  const hermesRun = useHermesRun(hermes.capabilities?.data ?? null);
  const selectedSkill = useMemo(() => selectedSkillId ? skillById[selectedSkillId] : null, [selectedSkillId]);
  const installedHermesIds = useMemo(() => new Set((hermes.skills.data ?? []).map((skill) => skill.id)), [hermes.skills.data]);
  const installationAvailable = hermes.skills.data !== null;
  const selectedInstallation = selectedSkill ? getAxionSkillInstallation(selectedSkill.id, installedHermesIds, installationAvailable) : "unavailable";
  const selectSession = useCallback((session: HermesSessionSummary, opener: HTMLButtonElement) => {
    setSelectedSession(session);
    setSessionOpener(opener);
  }, []);
  const closeSession = useCallback(() => setSelectedSession(null), []);

  return <div className="app-shell">
    <TopNavigation view={view} onViewChange={setView} query={query} onQueryChange={setQuery} gatewayStatus={hermes.gatewayStatus} />
    <AnimatePresence mode="wait">
      {view === "map" && <motion.main className="map-view" key="map" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
        <SkillTreeCanvas query={query} onSelectSkill={setSelectedSkillId} installedHermesIds={installedHermesIds} installationAvailable={installationAvailable} />
        <ActivityPanel sessions={hermes.sessions.data} loading={hermes.sessions.loading} error={hermes.sessions.error} onSelectSession={selectSession} onRefresh={() => { void hermes.sessions.refresh(); }} onOpenFull={() => setView("activity")} />
      </motion.main>}
      {view === "activity" && <motion.main className="activity-view" key="activity" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
        <div className="view-heading"><span>HERMES SESSIONS / READ-ONLY</span><h1>System activity</h1><p>Safe session metadata from the connected Hermes Agent.</p></div>
        <ActivityPanel sessions={hermes.sessions.data} loading={hermes.sessions.loading} error={hermes.sessions.error} expanded onSelectSession={selectSession} onRefresh={() => { void hermes.sessions.refresh(); }} />
      </motion.main>}
      {view === "dashboard" && <motion.div key="dashboard" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
        <DashboardOverview loading={hermes.overview.loading} data={hermes.overview.data} error={hermes.overview.error} lastSuccessAt={hermes.overview.lastSuccessAt} onRefresh={() => { void hermes.refreshAll(); }} readiness={hermes.health.data?.readiness === "ready" ? "Ready" : hermes.health.data?.readiness === "degraded" ? "Degraded" : undefined} />
      </motion.div>}
    </AnimatePresence>
    <SkillDetailDrawer skill={selectedSkill} installation={selectedInstallation} online={hermes.gatewayStatus === "online" || hermes.gatewayStatus === "degraded"} capabilities={hermes.capabilities?.data ?? null} submitting={hermesRun.submitting} onRunSkill={(opener) => { setRunOpener(opener); setRunDialogOpen(true); }} onClose={() => setSelectedSkillId(null)} />
    <RunSkillDialog open={runDialogOpen && Boolean(selectedSkill)} skillName={selectedSkill?.name ?? "skill"} submitting={hermesRun.submitting} error={hermesRun.error} onCancel={() => setRunDialogOpen(false)} onConfirm={async (task) => { if (!selectedSkill) return; await hermesRun.createRun(selectedSkill.id, selectedSkill.name, task); setRunDialogOpen(false); setSelectedSkillId(null); }} />
    {hermesRun.run && <RunProgressDrawer run={hermesRun.run} skillName={hermesRun.skillName} createdAt={hermesRun.createdAt} timeline={hermesRun.timeline} output={hermesRun.output} error={hermesRun.error} liveAvailable={Boolean(hermes.capabilities?.data?.runEventsSse)} connected={hermesRun.connected} canStop={Boolean(hermes.capabilities?.data?.runStop)} canApprove={Boolean(hermes.capabilities?.data?.runApprovalResponse && hermes.capabilities?.data?.approvalEvents)} stopping={hermesRun.stopping} approving={hermesRun.approving} opener={runOpener} onRefresh={hermesRun.refreshStatus} onApprove={(decision) => { void hermesRun.approve(decision); }} onStop={() => { void hermesRun.stop(); }} onClose={hermesRun.close} />}
    <SessionDetailDrawer session={selectedSession} opener={sessionOpener} onClose={closeSession} />
  </div>;
}
