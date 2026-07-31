import type { SkillInstallation } from "./types";

export const HERMES_SKILL_ALIASES = new Set(["verified-ai-radar", "verified-content-studio"]);

export function getAxionSkillInstallation(skillId: string, installedHermesIds: ReadonlySet<string>, available: boolean): SkillInstallation {
  if (!available) return "unavailable";
  return HERMES_SKILL_ALIASES.has(skillId) && installedHermesIds.has(skillId) ? "installed" : "prototype";
}
