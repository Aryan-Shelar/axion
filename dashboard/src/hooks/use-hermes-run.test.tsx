import { act, renderHook, waitFor } from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { RUN_STORAGE_KEY, useHermesRun } from "./use-hermes-run";

const capabilities = { runSubmission: true, runStatus: true, runEventsSse: false, runStop: true, runApprovalResponse: true, approvalEvents: true };
afterEach(() => { vi.restoreAllMocks(); localStorage.clear(); });

describe("useHermesRun recovery", () => {
  it("persists only minimal metadata and never the task", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(new Response(JSON.stringify({ data: { runId: "run_1", skillId: "verified-ai-radar", status: "starting" }, error: null, refreshedAt: new Date().toISOString() }), { headers: { "content-type": "application/json" } }));
    const { result } = renderHook(() => useHermesRun(capabilities)); await act(async () => { await result.current.createRun("verified-ai-radar", "AI Radar", "secret task text"); });
    const stored = localStorage.getItem(RUN_STORAGE_KEY)!; expect(stored).toContain("run_1"); expect(stored).toContain("AI Radar"); expect(stored).not.toContain("secret task text"); expect(stored).not.toContain("output");
  });

  it("clears recovery metadata with an invalid run ID without restarting", async () => {
    localStorage.setItem(RUN_STORAGE_KEY, JSON.stringify({ runId: "../bad", skillId: "x", skillName: "Bad", createdAt: Date.now() })); const fetchSpy = vi.spyOn(globalThis, "fetch");
    renderHook(() => useHermesRun(capabilities)); await waitFor(() => expect(localStorage.getItem(RUN_STORAGE_KEY)).toBeNull()); expect(fetchSpy).not.toHaveBeenCalled();
  });
});
