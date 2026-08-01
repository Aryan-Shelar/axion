export type HermesPath = "/health" | "/health/detailed" | "/v1/capabilities" | "/v1/models" | "/v1/skills" | "/v1/toolsets" | "/api/sessions";
export type HermesGatewayStatus = "checking" | "online" | "degraded" | "offline" | "authentication";
export type HermesErrorCode = "offline" | "authentication" | "unavailable";
export type HermesPublicError = { code: HermesErrorCode; message: string };
export type HermesHealth = { readiness: "ready" | "degraded"; status: string };
export type HermesSkillSummary = { id: string; name: string; description?: string };
export type HermesToolsetSummary = { id: string; name: string };
export type HermesSessionSummary = { id: string; title: string; source?: string; status?: string; updatedAt?: string };
export type HermesOverview = { profile: string | null; model: string | null; activeRuns: number | null; activeDelegations: number | null };
export type HermesDashboardOverview = HermesOverview & { installedSkillsCount: number | null; toolsetsCount: number | null; recentSessionsCount: number | null };
export type HermesEnvelope<T> = { data: T | null; error: HermesPublicError | null; refreshedAt: string | null };
export type SkillInstallation = "installed" | "prototype" | "unavailable";
export type HermesCapabilities = { runSubmission: boolean; runStatus: boolean; runEventsSse: boolean; runStop: boolean; runApprovalResponse: boolean; approvalEvents: boolean };
export type HermesRunStatus = "starting" | "queued" | "running" | "waiting_for_approval" | "stopping" | "completed" | "failed" | "cancelled" | "disconnected" | "unknown";
export type HermesApprovalRequest = { approvalId: string; title: string; summary: string; kind?: string; expiresAt?: string };
export type HermesApprovalDecision = "once" | "deny";
export type HermesRunSummary = { runId: string; skillId: string; status: HermesRunStatus; output?: string; error?: string; createdAt?: string; updatedAt?: string; approval?: HermesApprovalRequest };
export type HermesRunEvent =
  | { type: "status"; status: HermesRunStatus; label?: string }
  | { type: "progress"; label: string }
  | { type: "tool"; label: string; state: "started" | "completed" }
  | { type: "output_delta" | "output_final"; text: string }
  | { type: "approval_required"; approval: HermesApprovalRequest }
  | { type: "approval_resolved"; decision?: HermesApprovalDecision }
  | { type: "failure"; message: string };
