import { getRunCapabilities } from "@/lib/hermes/run-client";
import { normalizeCapabilities } from "@/lib/hermes/run-normalize";
import { runFailure, runSuccess } from "@/lib/hermes/run-route";
export async function GET(request: Request) { try { return runSuccess(normalizeCapabilities(await getRunCapabilities({ signal: request.signal }))); } catch (error) { return runFailure(error); } }
