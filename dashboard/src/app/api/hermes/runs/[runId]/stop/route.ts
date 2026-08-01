import { stopHermesRun } from "@/lib/hermes/run-client";
import { runFailure, runSuccess, validateJsonWrite } from "@/lib/hermes/run-route";
export async function POST(request: Request, context: { params: Promise<{ runId: string }> }) { try { const { runId } = await context.params; await validateJsonWrite(request, []); await stopHermesRun(runId, { signal: request.signal }); return runSuccess({ runId, status: "stopping" }); } catch (error) { return runFailure(error); } }
