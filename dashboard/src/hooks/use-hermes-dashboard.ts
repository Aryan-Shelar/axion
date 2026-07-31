"use client";

import { useCallback } from "react";
import type { HermesDashboardOverview, HermesGatewayStatus, HermesHealth, HermesSessionSummary, HermesSkillSummary, HermesToolsetSummary } from "@/lib/hermes/types";
import { useHermesResource } from "./use-hermes-resource";

export function useHermesDashboard() {
  const health = useHermesResource<HermesHealth>("/api/hermes/health", 15_000);
  const overview = useHermesResource<HermesDashboardOverview>("/api/hermes/overview", 30_000);
  const sessions = useHermesResource<HermesSessionSummary[]>("/api/hermes/sessions", 30_000);
  const skills = useHermesResource<HermesSkillSummary[]>("/api/hermes/skills", 60_000);
  const toolsets = useHermesResource<HermesToolsetSummary[]>("/api/hermes/toolsets", 60_000);
  const gatewayStatus: HermesGatewayStatus = health.loading ? "checking" : health.error?.code === "authentication" ? "authentication" : health.error?.code === "offline" ? "offline" : health.data?.readiness === "degraded" ? "degraded" : health.data ? "online" : "offline";
  const refreshAll = useCallback(async () => { await Promise.all([health.refresh(), overview.refresh(), sessions.refresh(), skills.refresh(), toolsets.refresh()]); }, [health.refresh, overview.refresh, sessions.refresh, skills.refresh, toolsets.refresh]);
  return { health, overview, sessions, skills, toolsets, gatewayStatus, refreshAll };
}
