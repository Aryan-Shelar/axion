import { getHermesRun } from "@/lib/hermes/run-client";
import { normalizeRunSummary } from "@/lib/hermes/run-normalize";
import { requireRunId, runFailure, runSuccess } from "@/lib/hermes/run-route";
export async function GET(request: Request, context: { params: Promise<{ runId: string }> }) { try { const params = await context.params; const runId = requireRunId(params.runId); return runSuccess(normalizeRunSummary(await getHermesRun(runId, { signal: request.signal }), "")); } catch (error) { return runFailure(error); } }
