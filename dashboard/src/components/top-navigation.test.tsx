import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { TopNavigation } from "./top-navigation";

describe("TopNavigation", () => {
  it("routes each navigation tab to its corresponding view", () => {
    const onViewChange = vi.fn();
    render(<TopNavigation view="map" onViewChange={onViewChange} query="" onQueryChange={() => undefined} />);

    fireEvent.click(screen.getByRole("button", { name: /activity/i }));
    fireEvent.click(screen.getByRole("button", { name: /dashboard/i }));
    fireEvent.click(screen.getByRole("button", { name: /^map$/i }));

    expect(onViewChange.mock.calls.map(([view]) => view)).toEqual(["activity", "dashboard", "map"]);
  });

  it("labels the gateway and all displayed metrics as demo data", () => {
    render(<TopNavigation view="map" onViewChange={() => undefined} query="" onQueryChange={() => undefined} />);
    expect(screen.getByText(/prototype/i)).toBeInTheDocument();
    expect(screen.getByText(/gateway demo/i)).toBeInTheDocument();
  });
});
