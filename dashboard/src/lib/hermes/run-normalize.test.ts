import { describe, expect, it } from "vitest";
import { MAX_APPROVAL_SUMMARY, MAX_OUTPUT_TEXT, isValidRunId, normalizeCapabilities, normalizeRunEvent, normalizeRunSummary } from "./run-normalize";

describe("Hermes run normalization", () => {
  it("feature-detects current and equivalent approval capability names", () => {
    expect(normalizeCapabilities({ features: { run_submission: true, run_status: true, run_events_sse: true, run_stop: true, run_approval_response: true, approval_events: true } })).toEqual({ runSubmission: true, runStatus: true, runEventsSse: true, runStop: true, runApprovalResponse: true, approvalEvents: true });
    expect(normalizeCapabilities({ features: { run_approval: true } }).runApprovalResponse).toBe(true);
  });

  it("normalizes statuses and bounds public output", () => {
    expect(normalizeRunSummary({ run_id: "run_1", status: "completed", output: "x".repeat(MAX_OUTPUT_TEXT + 20) }, "verified-ai-radar")).toEqual({ runId: "run_1", skillId: "verified-ai-radar", status: "completed", output: "x".repeat(MAX_OUTPUT_TEXT) });
    expect(normalizeRunSummary({ run_id: "run_2", status: "unexpected" }, "skill").status).toBe("unknown");
  });

  it("normalizes lifecycle, text, tool, approval, and unknown events safely", () => {
    expect(normalizeRunEvent({ event: "run.running" })).toMatchObject({ type: "status", status: "running" });
    expect(normalizeRunEvent({ event: "response.output_text.delta", delta: "hello" })).toEqual({ type: "output_delta", text: "hello" });
    expect(normalizeRunEvent({ event: "tool.start", name: "browser" })).toEqual({ type: "tool", label: "Started browser", state: "started" });
    expect(normalizeRunEvent({ event: "approval.request", approval_id: "approval_1", description: "s".repeat(MAX_APPROVAL_SUMMARY + 1), kind: "command" })).toEqual({ type: "approval_required", approval: { approvalId: "approval_1", title: "Sensitive action requires approval", summary: "s".repeat(MAX_APPROVAL_SUMMARY), kind: "command" } });
    expect(normalizeRunEvent({ event: "brand.new", secret: "do-not-leak" })).toEqual({ type: "progress", label: "Hermes reported progress." });
  });

  it("validates run IDs before path interpolation", () => {
    expect(isValidRunId("run_Abc-123")).toBe(true);
    expect(isValidRunId("../secret")).toBe(false);
    expect(isValidRunId("x".repeat(129))).toBe(false);
  });
});
