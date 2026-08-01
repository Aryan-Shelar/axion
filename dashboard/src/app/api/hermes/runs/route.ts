import { createValidatedRun, runFailure, runSuccess } from "@/lib/hermes/run-route";
export async function POST(request: Request) { try { return runSuccess(await createValidatedRun(request), 202); } catch (error) { return runFailure(error); } }
