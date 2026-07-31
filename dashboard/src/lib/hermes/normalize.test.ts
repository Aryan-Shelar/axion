import { describe, expect, it } from "vitest";
import { normalizeHealth, normalizeOverview, normalizeSessions, normalizeSkills, normalizeToolsets } from "./normalize";

describe("Hermes normalization", () => {
  it("normalizes readiness and advertised model/profile", () => {
    expect(normalizeHealth({ status: "ok", ready: true })).toMatchObject({ readiness: "ready" });
    expect(normalizeOverview({ capabilities: { profile: "local" }, models: { models: [{ id: "qwen3" }] }, detailed: { active_runs: 2, delegations: 1 } })).toMatchObject({ profile: "local", model: "qwen3", activeRuns: 2, activeDelegations: 1 });
  });

  it("rejects malformed collection responses", () => {
    expect(() => normalizeSkills({ skills: "private" })).toThrow();
    expect(() => normalizeToolsets(null)).toThrow();
    expect(() => normalizeSessions({ sessions: {} })).toThrow();
  });

  it("removes messages and sensitive fields from session summaries", () => {
    const sessions = normalizeSessions({ sessions: [{ id: "s1", title: "Planning", source: "hermes-cli", status: "active", updated_at: "2026-07-31", messages: [{ content: "secret" }], prompt: "private prompt", tool_arguments: { token: "hidden" }, output: "private output", api_key: "hidden", path: "C:/private" }] });
    expect(sessions).toEqual([{ id: "s1", title: "Planning", source: "hermes-cli", status: "active", updatedAt: "2026-07-31" }]);
    expect(JSON.stringify(sessions)).not.toMatch(/secret|hidden|private|messages|content|prompt|tool|argument|output|token|key|path/i);
  });

  it("normalizes skills and toolsets to minimal summaries", () => {
    expect(normalizeSkills({ skills: [{ id: "verified-ai-radar", name: "Radar", description: "Installed" }] })).toEqual([{ id: "verified-ai-radar", name: "Radar", description: "Installed" }]);
    expect(normalizeToolsets([{ id: "browser", name: "Browser" }])).toEqual([{ id: "browser", name: "Browser" }]);
  });
});
