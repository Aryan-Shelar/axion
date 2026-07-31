import { HermesRequestError } from "./errors";
import type { HermesHealth, HermesOverview, HermesSessionSummary, HermesSkillSummary, HermesToolsetSummary } from "./types";

type RecordValue = Record<string, unknown>;
const record = (value: unknown): RecordValue => {
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new HermesRequestError("malformed");
  return value as RecordValue;
};
const text = (value: unknown) => typeof value === "string" && value.trim() ? value : undefined;
const number = (value: unknown) => typeof value === "number" && Number.isFinite(value) ? value : null;
const collection = (value: unknown, key: string): unknown[] => {
  if (Array.isArray(value)) return value;
  const root = record(value);
  if (!Array.isArray(root[key])) throw new HermesRequestError("malformed");
  return root[key];
};

export function normalizeHealth(value: unknown): HermesHealth {
  const root = record(value);
  const status = text(root.status) ?? text(root.readiness) ?? "unknown";
  const ready = root.ready === true || ["ok", "ready", "healthy", "online"].includes(status.toLowerCase());
  return { readiness: ready ? "ready" : "degraded", status };
}

export function normalizeSkills(value: unknown): HermesSkillSummary[] {
  return collection(value, "skills").map((item) => {
    const entry = record(item); const id = text(entry.id) ?? text(entry.slug) ?? text(entry.name);
    if (!id) throw new HermesRequestError("malformed");
    return { id, name: text(entry.name) ?? id, ...(text(entry.description) ? { description: text(entry.description) } : {}) };
  });
}

export function normalizeToolsets(value: unknown): HermesToolsetSummary[] {
  return collection(value, "toolsets").map((item) => { const entry = record(item); const id = text(entry.id) ?? text(entry.name); if (!id) throw new HermesRequestError("malformed"); return { id, name: text(entry.name) ?? id }; });
}

export function normalizeSessions(value: unknown): HermesSessionSummary[] {
  return collection(value, "sessions").map((item) => {
    const entry = record(item); const id = text(entry.id) ?? text(entry.session_id); if (!id) throw new HermesRequestError("malformed");
    return { id, title: text(entry.title) ?? text(entry.name) ?? `Session ${id}`, ...(text(entry.status) ? { status: text(entry.status) } : {}), ...(text(entry.updated_at) ?? text(entry.updatedAt) ? { updatedAt: text(entry.updated_at) ?? text(entry.updatedAt) } : {}) };
  });
}

export function normalizeOverview(parts: { capabilities?: unknown; models?: unknown; detailed?: unknown }): HermesOverview {
  const capabilities = parts.capabilities ? record(parts.capabilities) : {};
  const modelsRoot = parts.models ? (Array.isArray(parts.models) ? { models: parts.models } : record(parts.models)) : {};
  const models = Array.isArray(modelsRoot.models) ? modelsRoot.models : [];
  const firstModel = models[0] && typeof models[0] === "object" ? models[0] as RecordValue : {};
  const detailed = parts.detailed ? record(parts.detailed) : {};
  return { profile: text(capabilities.profile) ?? text(capabilities.name) ?? null, model: text(firstModel.id) ?? text(firstModel.name) ?? text(modelsRoot.model) ?? null, activeRuns: number(detailed.active_runs ?? detailed.activeRuns), activeDelegations: number(detailed.delegations ?? detailed.active_delegations ?? detailed.activeDelegations) };
}
