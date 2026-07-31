import { describe, expect, it } from "vitest";
import { getAxionSkillInstallation } from "./skill-aliases";

describe("Hermes skill aliases", () => {
  it("matches only the two exact Phase A aliases", () => {
    const installed = new Set(["verified-ai-radar", "verified-content-studio", "Verified-AI-Radar"]);
    expect(getAxionSkillInstallation("verified-ai-radar", installed, true)).toBe("installed");
    expect(getAxionSkillInstallation("verified-content-studio", installed, true)).toBe("installed");
    expect(getAxionSkillInstallation("carousel-builder", installed, true)).toBe("prototype");
    expect(getAxionSkillInstallation("Verified-AI-Radar", installed, true)).toBe("prototype");
  });

  it("reports unavailable when Hermes skill data cannot be read", () => {
    expect(getAxionSkillInstallation("verified-ai-radar", new Set(), false)).toBe("unavailable");
  });
});
