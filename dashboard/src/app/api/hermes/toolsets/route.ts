import { normalizeToolsets } from "@/lib/hermes/normalize";
import { handleHermesRoute } from "@/lib/hermes/route-response";

export async function GET() { return handleHermesRoute("/v1/toolsets", normalizeToolsets); }
