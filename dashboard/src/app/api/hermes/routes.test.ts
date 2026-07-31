import { beforeEach, describe, expect, it, vi } from "vitest";
import { HermesRequestError } from "@/lib/hermes/errors";
import { handleHermesRoute } from "@/lib/hermes/route-response";
import { normalizeSkills } from "@/lib/hermes/normalize";

const { hermesGet } = vi.hoisted(() => ({ hermesGet: vi.fn() }));
vi.mock("@/lib/hermes/client", () => ({ hermesGet }));
import { GET as getHealth } from "./health/route";
import { GET as getOverview } from "./overview/route";
import { GET as getSessions } from "./sessions/route";

beforeEach(() => hermesGet.mockReset());

describe("Hermes API routes", () => {
  it("returns normalized health success", async () => {
    hermesGet.mockResolvedValue({ status: "ok", ready: true });
    const response = await getHealth();
    expect(response.status).toBe(200);
    expect(await response.json()).toMatchObject({ data: { readiness: "ready" }, error: null });
  });

  it("returns a safe authentication failure", async () => {
    const request = async () => { throw new HermesRequestError("auth", 401, "secret upstream body"); };
    const response = await handleHermesRoute("/v1/skills", normalizeSkills, request);
    expect(response.status).toBe(401);
    expect(await response.json()).toEqual({ data: null, error: { code: "authentication", message: "Hermes authentication failed." }, refreshedAt: null });
  });

  it("keeps successful overview panels when another upstream endpoint fails", async () => {
    hermesGet.mockImplementation(async (path: string) => {
      if (path === "/v1/models") throw new TypeError("connection refused C:/private");
      if (path === "/health/detailed") return { active_runs: 2 };
      if (path === "/v1/capabilities") return { profile: "local" };
      if (path === "/v1/skills") return { skills: [{ id: "verified-ai-radar", name: "Radar" }] };
      if (path === "/v1/toolsets") return { toolsets: [{ id: "browser", name: "Browser" }] };
      return { sessions: [{ id: "s1", title: "One", messages: [{ content: "secret" }] }] };
    });
    const response = await getOverview();
    const body = await response.json();
    expect(body.data).toMatchObject({ profile: "local", model: null, installedSkillsCount: 1, toolsetsCount: 1, recentSessionsCount: 1, activeRuns: 2 });
    expect(body.panels.models.error.code).toBe("offline");
    expect(JSON.stringify(body)).not.toContain("secret");
  });

  it("normalizes sessions without message contents", async () => {
    hermesGet.mockResolvedValue({ sessions: [{ id: "s1", title: "One", messages: [{ content: "private" }] }] });
    const body = await (await getSessions()).json();
    expect(body.data).toEqual([{ id: "s1", title: "One" }]);
    expect(JSON.stringify(body)).not.toContain("private");
  });
});
