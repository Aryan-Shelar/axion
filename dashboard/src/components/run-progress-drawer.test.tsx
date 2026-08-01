import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RunProgressDrawer } from "./run-progress-drawer";

const run = { runId: "run_1", skillId: "verified-ai-radar", status: "running" as const };
const base = { run, skillName: "AI Radar", createdAt: Date.now(), timeline: [], output: "", error: null, liveAvailable: true, connected: true, canStop: true, canApprove: true, stopping: false, approving: false, onRefresh: vi.fn(), onApprove: vi.fn(), onStop: vi.fn(), onClose: vi.fn() };

describe("RunProgressDrawer", () => {
  it("renders semantic running and completed states without raw JSON", () => {
    const { rerender } = render(<RunProgressDrawer {...base} />); expect(screen.getByRole("dialog", { name: "AI Radar run progress" })).toHaveTextContent("Running"); expect(screen.getByText("run_1")).toBeInTheDocument();
    rerender(<RunProgressDrawer {...base} run={{ ...run, status: "completed" }} output="Finished safely" />); expect(screen.getByText("Finished safely")).toBeInTheDocument(); expect(screen.getByRole("button", { name: "Close" })).toBeInTheDocument();
  });

  it("shows only Approve once and Deny for a supported approval", () => {
    render(<RunProgressDrawer {...base} run={{ ...run, status: "waiting_for_approval", approval: { approvalId: "a1", title: "Sensitive action requires approval", summary: "Write a file" } }} />);
    expect(screen.getByRole("button", { name: "Approve once" })).toBeInTheDocument(); expect(screen.getByRole("button", { name: "Deny" })).toBeInTheDocument(); expect(screen.queryByText(/always|session|yolo/i)).not.toBeInTheDocument();
  });

  it("confirms stop and does not claim cancellation early", () => {
    const stop = vi.fn(); render(<RunProgressDrawer {...base} onStop={stop} />); fireEvent.click(screen.getByRole("button", { name: "Stop Run" })); expect(screen.getByText("Stop this Hermes run?")).toBeInTheDocument(); fireEvent.click(screen.getByRole("button", { name: "Confirm Stop" })); expect(stop).toHaveBeenCalledOnce(); expect(screen.queryByText("Cancelled")).not.toBeInTheDocument();
  });

  it("explains polling fallback and unsupported approval", () => {
    render(<RunProgressDrawer {...base} liveAvailable={false} canApprove={false} run={{ ...run, status: "waiting_for_approval", approval: { approvalId: "a1", title: "Sensitive action requires approval", summary: "Write" } }} />);
    expect(screen.getByText("Live updates unavailable")).toBeInTheDocument(); expect(screen.getByText(/cannot resolve this approval request/i)).toBeInTheDocument(); expect(screen.queryByRole("button", { name: "Approve once" })).not.toBeInTheDocument();
  });
});
