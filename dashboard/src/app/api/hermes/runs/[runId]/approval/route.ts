import { respondHermesApproval } from "@/lib/hermes/run-client";
import { parseApprovalRequest, runFailure, runSuccess, validateJsonWrite } from "@/lib/hermes/run-route";
export async function POST(request: Request, context: { params: Promise<{ runId: string }> }) { try { const { runId } = await context.params; const decision = parseApprovalRequest(await validateJsonWrite(request, ["decision"])); await respondHermesApproval(runId, decision, { signal: request.signal }); return runSuccess({ runId, status: "running", decision }); } catch (error) { return runFailure(error); } }
