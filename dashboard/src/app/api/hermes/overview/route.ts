import { hermesGet } from "@/lib/hermes/client";
import { toPublicHermesError } from "@/lib/hermes/errors";
import { normalizeOverview, normalizeSessions, normalizeSkills, normalizeToolsets } from "@/lib/hermes/normalize";

const paths = ["/v1/capabilities", "/v1/models", "/health/detailed", "/v1/skills", "/v1/toolsets", "/api/sessions"] as const;
const names = ["capabilities", "models", "detailed", "skills", "toolsets", "sessions"] as const;

export async function GET() {
  const settled = await Promise.allSettled(paths.map((path) => hermesGet(path)));
  const values: Record<string, unknown> = {};
  const panels: Record<string, { error: ReturnType<typeof toPublicHermesError> | null }> = {};
  settled.forEach((result, index) => {
    const name = names[index];
    if (result.status === "fulfilled") { values[name] = result.value; panels[name] = { error: null }; }
    else panels[name] = { error: toPublicHermesError(result.reason) };
  });
  const overview = normalizeOverview({ capabilities: values.capabilities, models: values.models, detailed: values.detailed });
  const safeCount = (name: string, normalize: (value: unknown) => unknown[]) => {
    if (!(name in values)) return null;
    try { return normalize(values[name]).length; } catch (error) { panels[name] = { error: toPublicHermesError(error) }; return null; }
  };
  const data = { ...overview, installedSkillsCount: safeCount("skills", normalizeSkills), toolsetsCount: safeCount("toolsets", normalizeToolsets), recentSessionsCount: safeCount("sessions", normalizeSessions) };
  return Response.json({ data, panels, error: null, refreshedAt: new Date().toISOString() });
}
