import { normalizeSkills } from "@/lib/hermes/normalize";
import { handleHermesRoute } from "@/lib/hermes/route-response";

export async function GET() { return handleHermesRoute("/v1/skills", normalizeSkills); }
