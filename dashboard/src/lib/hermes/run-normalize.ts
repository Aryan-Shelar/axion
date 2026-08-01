import { HermesRequestError } from "./errors";
import type { HermesApprovalRequest, HermesCapabilities, HermesRunEvent, HermesRunStatus, HermesRunSummary } from "./types";

export const MAX_TIMELINE_EVENTS = 200;
export const MAX_OUTPUT_TEXT = 50_000;
export const MAX_APPROVAL_SUMMARY = 1_000;
export const RUN_ID_PATTERN = /^[A-Za-z0-9_-]{1,128}$/;
const STATUSES = new Set<HermesRunStatus>(["starting", "queued", "running", "waiting_for_approval", "stopping", "completed", "failed", "cancelled", "disconnected", "unknown"]);
const record = (value: unknown): Record<string, unknown> => { if (!value || typeof value !== "object" || Array.isArray(value)) throw new HermesRequestError("malformed"); return value as Record<string, unknown>; };
const string = (value: unknown, limit: number) => typeof value === "string" && value.trim() ? value.slice(0, limit) : undefined;
const status = (value: unknown): HermesRunStatus => typeof value === "string" && STATUSES.has(value as HermesRunStatus) ? value as HermesRunStatus : "unknown";

export const isValidRunId = (value: unknown): value is string => typeof value === "string" && RUN_ID_PATTERN.test(value);

export function normalizeCapabilities(value: unknown): HermesCapabilities {
  const root = record(value); const features = root.features && typeof root.features === "object" && !Array.isArray(root.features) ? root.features as Record<string, unknown> : root;
  return { runSubmission: features.run_submission === true, runStatus: features.run_status === true, runEventsSse: features.run_events_sse === true, runStop: features.run_stop === true, runApprovalResponse: features.run_approval_response === true || features.run_approval === true, approvalEvents: features.approval_events === true };
}

function approval(value: Record<string, unknown>): HermesApprovalRequest | undefined {
  const approvalId = string(value.approval_id ?? value.approvalId, 128); if (!approvalId) return undefined;
  return { approvalId, title: string(value.title, 120) ?? "Sensitive action requires approval", summary: string(value.description ?? value.summary ?? value.command, MAX_APPROVAL_SUMMARY) ?? "Hermes requested approval for a sensitive action.", ...(string(value.kind, 80) ? { kind: string(value.kind, 80) } : {}), ...(string(value.expires_at ?? value.expiresAt, 80) ? { expiresAt: string(value.expires_at ?? value.expiresAt, 80) } : {}) };
}

export function normalizeRunSummary(value: unknown, skillId: string): HermesRunSummary {
  const root = record(value); const runId = string(root.run_id ?? root.runId, 128); if (!runId || !isValidRunId(runId)) throw new HermesRequestError("malformed");
  const result: HermesRunSummary = { runId, skillId, status: status(root.status) };
  const output = string(root.output, MAX_OUTPUT_TEXT); const error = string(root.error ?? root.message, 500); const pending = root.approval && typeof root.approval === "object" ? approval(root.approval as Record<string, unknown>) : undefined;
  if (output) result.output = output; if (error && result.status === "failed") result.error = error; if (pending) result.approval = pending;
  const createdAt = string(root.created_at ?? root.createdAt, 80); const updatedAt = string(root.updated_at ?? root.updatedAt, 80); if (createdAt) result.createdAt = createdAt; if (updatedAt) result.updatedAt = updatedAt;
  return result;
}

export function normalizeRunEvent(value: unknown): HermesRunEvent | null {
  const root = record(value); const event = string(root.event ?? root.type, 120)?.toLowerCase(); if (!event) return null;
  const statusMatch = event.match(/(?:run\.)?(starting|queued|running|waiting_for_approval|stopping|completed|failed|cancelled)$/);
  if (statusMatch) return { type: "status", status: status(statusMatch[1]), ...(string(root.label, 200) ? { label: string(root.label, 200) } : {}) };
  if (event === "response.output_text.delta" || event === "text.delta" || event === "output.delta") return string(root.delta ?? root.text, MAX_OUTPUT_TEXT) ? { type: "output_delta", text: string(root.delta ?? root.text, MAX_OUTPUT_TEXT)! } : null;
  if (["response.completed", "run.output", "output.final"].includes(event)) return string(root.output ?? root.text, MAX_OUTPUT_TEXT) ? { type: "output_final", text: string(root.output ?? root.text, MAX_OUTPUT_TEXT)! } : { type: "status", status: "completed" };
  if (["approval.request", "approval.required", "hermes.approval.request"].includes(event)) { const normalized = approval(root); return normalized ? { type: "approval_required", approval: normalized } : { type: "progress", label: "Hermes requested approval." }; }
  if (["approval.responded", "approval.resolved"].includes(event)) { const choice = root.choice === "once" || root.choice === "deny" ? root.choice : undefined; return { type: "approval_resolved", ...(choice ? { decision: choice } : {}) }; }
  if (event.includes("tool") && (event.includes("start") || event.includes("added"))) return { type: "tool", label: `Started ${string(root.name ?? root.tool_name, 100) ?? "tool"}`, state: "started" };
  if (event.includes("tool") && (event.includes("complete") || event.includes("done"))) return { type: "tool", label: `Completed ${string(root.name ?? root.tool_name, 100) ?? "tool"}`, state: "completed" };
  if (event.includes("fail") || event.includes("error")) return { type: "failure", message: string(root.message, 500) ?? "Hermes reported that the run failed." };
  return { type: "progress", label: "Hermes reported progress." };
}
