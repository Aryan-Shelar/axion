import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import Home from "./page";

const refreshSessions = vi.fn();
const sessions = [
  { id: "one", title: "First session", updatedAt: "2026-07-31T12:00:00Z" },
  { id: "two", title: "Second session", updatedAt: "2026-07-31T11:00:00Z" },
  { id: "three", title: "Third session", updatedAt: "2026-07-31T10:00:00Z" },
  { id: "four", title: "Fourth session", updatedAt: "2026-07-31T09:00:00Z" },
];

vi.mock("@/components/skill-tree-canvas", () => ({ SkillTreeCanvas: () => <div>Skill tree map</div> }));
vi.mock("@/hooks/use-hermes-dashboard", () => ({
  useHermesDashboard: () => ({
    health: { data: { readiness: "ready" }, loading: false, error: null },
    overview: { data: null, loading: false, error: null, lastSuccessAt: null },
    sessions: { data: sessions, loading: false, error: null, refresh: refreshSessions },
    skills: { data: [], loading: false, error: null },
    toolsets: { data: [], loading: false, error: null },
    capabilities: { data: { runSubmission: true, runStatus: true, runEventsSse: true, runStop: true, runApprovalResponse: true, approvalEvents: true }, loading: false, error: null },
    gatewayStatus: "online",
    refreshAll: vi.fn(),
  }),
}));

describe("Home Hermes activity integration", () => {
  it("switches the compact Map panel to the full real Activity view", async () => {
    render(<Home />);
    expect(screen.getAllByRole("button", { name: /session$/i })).toHaveLength(3);
    fireEvent.click(screen.getByRole("button", { name: "Open full activity" }));
    expect(await screen.findByRole("heading", { name: "System activity" })).toBeInTheDocument();
    expect(screen.getAllByRole("button", { name: /session$/i })).toHaveLength(4);
    fireEvent.click(screen.getByRole("button", { name: "Refresh Hermes activity" }));
    expect(refreshSessions).toHaveBeenCalledOnce();
  });

  it("opens a selected session in the read-only drawer", () => {
    render(<Home />);
    fireEvent.click(screen.getByRole("button", { name: "Open First session" }));
    expect(screen.getByRole("dialog", { name: "First session details" })).toHaveTextContent("one");
  });
});
