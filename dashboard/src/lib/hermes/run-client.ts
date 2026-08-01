import "server-only";
import { HermesRequestError } from "./errors";
import { isValidRunId } from "./run-normalize";
import type { HermesApprovalDecision } from "./types";

const DEFAULT_HERMES_URL = "http://127.0.0.1:8642";
const TIMEOUT_MS = 10_000;
type Options = { signal?: AbortSignal; fetchImpl?: typeof fetch };

function pathFor(runId: string, suffix = "") { if (!isValidRunId(runId)) throw new Error("Invalid run ID"); return `/v1/runs/${runId}${suffix}`; }

async function request(path: string, method: "GET" | "POST", options: Options & { body?: unknown; headers?: Record<string, string>; stream?: boolean } = {}) {
  const controller = new AbortController(); let timedOut = false;
  const externalAbort = () => controller.abort(options.signal?.reason); options.signal?.addEventListener("abort", externalAbort, { once: true });
  const timeout = setTimeout(() => { timedOut = true; controller.abort(); }, TIMEOUT_MS);
  const headers = new Headers({ accept: options.stream ? "text/event-stream" : "application/json", ...options.headers });
  if (options.body !== undefined) headers.set("content-type", "application/json");
  if (process.env.HERMES_API_KEY) headers.set("authorization", `Bearer ${process.env.HERMES_API_KEY}`);
  try {
    const response = await (options.fetchImpl ?? fetch)(`${(process.env.HERMES_API_URL || DEFAULT_HERMES_URL).replace(/\/+$/, "")}${path}`, { method, headers, ...(options.body !== undefined ? { body: JSON.stringify(options.body) } : {}), cache: "no-store", signal: controller.signal });
    if (response.status === 401 || response.status === 403) throw new HermesRequestError("auth", response.status);
    if (!response.ok) throw new HermesRequestError("http", response.status);
    if (options.stream) { if (!response.body) throw new HermesRequestError("malformed", response.status); return response; }
    try { return await response.json(); } catch { throw new HermesRequestError("malformed", response.status); }
  } catch (error) { if (timedOut) throw new HermesRequestError("timeout"); throw error; }
  finally { clearTimeout(timeout); options.signal?.removeEventListener("abort", externalAbort); }
}

export const getRunCapabilities = (options?: Options) => request("/v1/capabilities", "GET", options);
export const getInstalledRunSkills = (options?: Options) => request("/v1/skills", "GET", options);
export const createHermesRun = (input: { input: string; instructions: string; sessionId: string; idempotencyKey: string }, options: Options = {}) => request("/v1/runs", "POST", { ...options, body: { input: input.input, instructions: input.instructions, session_id: input.sessionId }, headers: { "Idempotency-Key": input.idempotencyKey } });
export async function getHermesRun(runId: string, options?: Options) { return request(pathFor(runId), "GET", options); }
export const openHermesRunEvents = (runId: string, options: Options = {}) => request(pathFor(runId, "/events"), "GET", { ...options, stream: true }) as Promise<Response>;
export const respondHermesApproval = (runId: string, decision: HermesApprovalDecision, options: Options = {}) => request(pathFor(runId, "/approval"), "POST", { ...options, body: { choice: decision } });
export const stopHermesRun = (runId: string, options: Options = {}) => request(pathFor(runId, "/stop"), "POST", { ...options, body: {} });
