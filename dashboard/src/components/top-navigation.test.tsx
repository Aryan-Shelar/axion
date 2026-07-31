import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TopNavigation } from "./top-navigation";

const renderNav = (gatewayStatus: "checking" | "online" | "degraded" | "offline" | "authentication" = "checking") => render(<TopNavigation view="map" onViewChange={() => undefined} query="" onQueryChange={() => undefined} gatewayStatus={gatewayStatus} />);

describe("TopNavigation", () => {
  it("routes each navigation tab to its corresponding view", () => {
    const onViewChange = vi.fn();
    render(<TopNavigation view="map" onViewChange={onViewChange} query="" onQueryChange={() => undefined} gatewayStatus="online" />);

    fireEvent.click(screen.getByRole("button", { name: /activity/i }));
    fireEvent.click(screen.getByRole("button", { name: /dashboard/i }));
    fireEvent.click(screen.getByRole("button", { name: /^map$/i }));

    expect(onViewChange.mock.calls.map(([view]) => view)).toEqual(["activity", "dashboard", "map"]);
  });

  it.each([
    ["checking", "Checking Hermes"], ["online", "Hermes Online"], ["degraded", "Hermes Degraded"], ["offline", "Hermes Offline"], ["authentication", "Authentication Error"],
  ] as const)("renders %s gateway state", (state, label) => { renderNav(state); expect(screen.getByText(label)).toBeInTheDocument(); });
});
