import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import type { HermesSessionSummary } from "@/lib/hermes/types";
import { ActivityPanel } from "./activity-panel";

const sessions: HermesSessionSummary[] = [
  { id: "old", title: "Older Hermes session", status: "idle", updatedAt: "2026-07-30T10:00:00Z" },
  { id: "new", title: "Newest Hermes session", source: "desktop", status: "active", updatedAt: "2026-07-31T10:00:00Z" },
];
const base = { sessions, loading: false, error: null, onSelectSession: vi.fn(), onRefresh: vi.fn() };

describe("ActivityPanel", () => {
  it("renders real sessions newest first with safe metadata", () => {
    render(<ActivityPanel {...base} expanded />);
    const rows = screen.getAllByRole("button", { name: /Hermes session/i });
    expect(rows.map((row) => row.textContent)).toEqual([expect.stringContaining("Newest"), expect.stringContaining("Older")]);
    expect(screen.getByText("desktop")).toBeInTheDocument();
    expect(screen.queryByText(/Business Discovery discovered/i)).not.toBeInTheDocument();
  });

  it("shows loading, exact empty, offline, and authentication states", () => {
    const { rerender } = render(<ActivityPanel {...base} sessions={null} loading />);
    expect(screen.getByText(/Loading Hermes activity/i)).toBeInTheDocument();
    rerender(<ActivityPanel {...base} sessions={[]} />);
    expect(screen.getByText("No Hermes activity yet.")).toBeInTheDocument();
    rerender(<ActivityPanel {...base} sessions={null} error={{ code: "offline", message: "Hermes is unavailable." }} />);
    expect(screen.getByText("Hermes is unavailable.")).toBeInTheDocument();
    rerender(<ActivityPanel {...base} sessions={null} error={{ code: "authentication", message: "Hermes authentication failed." }} />);
    expect(screen.getByText("Hermes authentication failed.")).toBeInTheDocument();
  });

  it("keeps retained sessions visible with a non-blocking warning", () => {
    render(<ActivityPanel {...base} error={{ code: "offline", message: "Hermes is unavailable." }} />);
    expect(screen.getByText("Hermes is unavailable.")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Newest Hermes session/i })).toBeInTheDocument();
  });

  it("opens a session by mouse, Enter, and Space and refreshes manually", () => {
    const onSelectSession = vi.fn(); const onRefresh = vi.fn();
    render(<ActivityPanel {...base} expanded onSelectSession={onSelectSession} onRefresh={onRefresh} />);
    const row = screen.getByRole("button", { name: /Newest Hermes session/i });
    fireEvent.click(row); fireEvent.keyDown(row, { key: "Enter" }); fireEvent.keyDown(row, { key: " " });
    expect(onSelectSession).toHaveBeenCalledTimes(3);
    expect(onSelectSession.mock.calls[0][0].id).toBe("new");
    fireEvent.click(screen.getByRole("button", { name: "Refresh Hermes activity" }));
    expect(onRefresh).toHaveBeenCalledOnce();
  });

  it("renders no message content, secrets, or write controls", () => {
    render(<ActivityPanel {...base} expanded />);
    expect(screen.queryByText(/message|secret|prompt|output/i)).not.toBeInTheDocument();
    expect(screen.queryByRole("button", { name: /delete|edit|resume|stop|run/i })).not.toBeInTheDocument();
  });

  it("shows only the three newest compact sessions and opens the full Activity view", () => {
    const onOpenFull = vi.fn();
    const compactSessions = [
      ...sessions,
      { id: "middle", title: "Middle Hermes session", updatedAt: "2026-07-31T09:00:00Z" },
      { id: "latest", title: "Latest Hermes session", updatedAt: "2026-07-31T11:00:00Z" },
    ];
    render(<ActivityPanel {...base} sessions={compactSessions} onOpenFull={onOpenFull} />);
    expect(screen.getAllByRole("button", { name: /Hermes session/i })).toHaveLength(3);
    expect(screen.queryByRole("button", { name: /Older Hermes session/i })).not.toBeInTheDocument();
    fireEvent.click(screen.getByRole("button", { name: "Open full activity" }));
    expect(onOpenFull).toHaveBeenCalledOnce();
  });
});
