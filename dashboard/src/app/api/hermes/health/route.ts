import { normalizeHealth } from "@/lib/hermes/normalize";
import { handleHermesRoute } from "@/lib/hermes/route-response";

export async function GET() { return handleHermesRoute("/health", normalizeHealth); }
