import { stopHermesRun } from "@/lib/hermes/run-client";
import { requireRunId, runFailure, runSuccess, validateJsonWrite } from "@/lib/hermes/run-route";
export async function POST(request: Request, context: { params: Promise<{ runId: string }> }) { try { const params = await context.params; const runId = requireRunId(params.runId); await validateJsonWrite(request, []); await stopHermesRun(runId, { signal: request.signal }); return runSuccess({ runId, status: "stopping" }); } catch (error) { return runFailure(error); } }
