import { getHermesRun } from "@/lib/hermes/run-client";
import { normalizeRunSummary } from "@/lib/hermes/run-normalize";
import { runFailure, runSuccess } from "@/lib/hermes/run-route";
export async function GET(request: Request, context: { params: Promise<{ runId: string }> }) { try { const { runId } = await context.params; return runSuccess(normalizeRunSummary(await getHermesRun(runId, { signal: request.signal }), "")); } catch (error) { return runFailure(error); } }
