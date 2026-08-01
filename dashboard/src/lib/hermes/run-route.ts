import { randomUUID } from "node:crypto";
import { toPublicHermesError } from "./errors";
import { HERMES_SKILL_ALIASES } from "./skill-aliases";
import { normalizeCapabilities, normalizeRunSummary } from "./run-normalize";
import { normalizeSkills } from "./normalize";
import { createHermesRun, getInstalledRunSkills, getRunCapabilities } from "./run-client";
import type { HermesApprovalDecision, HermesRunSummary } from "./types";

export class RunRouteError extends Error { constructor(public status: number, message: string) { super(message); } }
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/i;
const pending = new Map<string, Promise<HermesRunSummary>>();

export async function validateJsonWrite(request: Request, allowedFields: readonly string[]) {
  if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) throw new RunRouteError(415, "Content-Type must be application/json.");
  const origin = request.headers.get("origin"); if (origin && origin !== new URL(request.url).origin) throw new RunRouteError(403, "Cross-origin requests are not allowed.");
  let value: unknown; try { value = await request.json(); } catch { throw new RunRouteError(400, "Request body must be valid JSON."); }
  if (!value || typeof value !== "object" || Array.isArray(value)) throw new RunRouteError(400, "Request body must be a JSON object.");
  const unknown = Object.keys(value).filter((key) => !allowedFields.includes(key)); if (unknown.length) throw new RunRouteError(400, "Request contains unsupported fields.");
  return value as Record<string, unknown>;
}

export function parseCreateRunRequest(value: Record<string, unknown>) {
  const skillId = typeof value.skillId === "string" ? value.skillId : ""; const task = typeof value.task === "string" ? value.task.trim() : ""; const idempotencyKey = typeof value.idempotencyKey === "string" ? value.idempotencyKey : "";
  if (!skillId || task.length < 3 || task.length > 4000 || !UUID.test(idempotencyKey)) throw new RunRouteError(400, "Invalid skill, task, or idempotency key.");
  return { skillId, task, idempotencyKey };
}
export function parseApprovalRequest(value: Record<string, unknown>): HermesApprovalDecision { if (value.decision !== "once" && value.decision !== "deny") throw new RunRouteError(400, "Decision must be once or deny."); return value.decision; }

export const runSuccess = <T>(data: T, status = 200) => Response.json({ data, error: null, refreshedAt: new Date().toISOString() }, { status });
export function runFailure(error: unknown) { if (error instanceof RunRouteError) return Response.json({ data: null, error: { code: "unavailable", message: error.message }, refreshedAt: null }, { status: error.status }); const safe = toPublicHermesError(error); return Response.json({ data: null, error: safe, refreshedAt: null }, { status: safe.code === "authentication" ? 401 : 503 }); }

export async function createValidatedRun(request: Request): Promise<HermesRunSummary> {
  const input = parseCreateRunRequest(await validateJsonWrite(request, ["skillId", "task", "idempotencyKey"]));
  if (!HERMES_SKILL_ALIASES.has(input.skillId)) throw new RunRouteError(400, "This skill is not trusted for execution.");
  const existing = pending.get(input.idempotencyKey); if (existing) return existing;
  const operation = (async () => {
    const [capRaw, skillsRaw] = await Promise.all([getRunCapabilities({ signal: request.signal }), getInstalledRunSkills({ signal: request.signal })]);
    if (!normalizeCapabilities(capRaw).runSubmission) throw new RunRouteError(409, "Connected Hermes does not support run submission.");
    if (!normalizeSkills(skillsRaw).some((skill) => skill.id === input.skillId)) throw new RunRouteError(409, "This trusted skill is not currently installed in Hermes.");
    const instructions = `You are executing the AXION skill \`${input.skillId}\`. Use the installed Hermes skill \`${input.skillId}\` as the primary workflow for this task. Follow its safety rules. Do not claim an action succeeded unless it actually completed.`;
    const raw = await createHermesRun({ input: input.task, instructions, sessionId: `axion_${randomUUID()}`, idempotencyKey: input.idempotencyKey }, { signal: request.signal });
    const root = raw as Record<string, unknown>; return normalizeRunSummary({ ...root, status: root.status === "started" ? "starting" : root.status }, input.skillId);
  })(); pending.set(input.idempotencyKey, operation); operation.finally(() => setTimeout(() => pending.delete(input.idempotencyKey), 60_000)); return operation;
}
