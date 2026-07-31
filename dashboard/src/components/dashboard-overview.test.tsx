import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { DashboardOverview } from "./dashboard-overview";

it("renders independent Hermes overview metrics and manual refresh", () => {
  const refresh = vi.fn();
  render(<DashboardOverview loading={false} error={null} data={{ profile: "local", model: "qwen3", activeRuns: 2, activeDelegations: 1, installedSkillsCount: 2, toolsetsCount: 4, recentSessionsCount: 6 }} lastSuccessAt="2026-07-31T10:00:00Z" onRefresh={refresh} />);
  for (const value of ["Ready", "local", "qwen3", "2", "4", "6", "3"]) expect(screen.getByText(value)).toBeInTheDocument();
  fireEvent.click(screen.getByRole("button", { name: "Refresh Hermes data" }));
  expect(refresh).toHaveBeenCalledOnce();
});

describe("DashboardOverview availability", () => {
  it("shows loading state", () => { render(<DashboardOverview loading data={null} error={null} lastSuccessAt={null} onRefresh={() => undefined} />); expect(screen.getByText(/loading Hermes overview/i)).toBeInTheDocument(); });
  it("shows offline state without raw detail", () => { render(<DashboardOverview loading={false} data={null} error={{ code: "offline", message: "Hermes is unavailable." }} lastSuccessAt={null} onRefresh={() => undefined} />); expect(screen.getByText("Hermes is unavailable.")).toBeInTheDocument(); });
});
