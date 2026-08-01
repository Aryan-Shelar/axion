import React from "react";
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import { RunSkillDialog } from "./run-skill-dialog";

describe("RunSkillDialog", () => {
  it("focuses the exact required task field and validates its bounds", () => {
    render(<RunSkillDialog open skillName="AI Radar" submitting={false} error={null} onCancel={() => undefined} onConfirm={() => undefined} />);
    const field = screen.getByLabelText("What should this skill do?"); expect(field).toHaveFocus(); expect(field).toHaveAttribute("maxlength", "4000");
    expect(screen.getByRole("button", { name: "Confirm & Run" })).toBeDisabled(); fireEvent.change(field, { target: { value: "ab" } }); expect(screen.getByText("2 / 4000")).toBeInTheDocument(); expect(screen.getByRole("button", { name: "Confirm & Run" })).toBeDisabled();
    fireEvent.change(field, { target: { value: "abc" } }); expect(screen.getByRole("button", { name: "Confirm & Run" })).toBeEnabled();
  });

  it("submits a double click exactly once", async () => {
    const confirm = vi.fn(async () => undefined); render(<RunSkillDialog open skillName="AI Radar" submitting={false} error={null} onCancel={() => undefined} onConfirm={confirm} />);
    fireEvent.change(screen.getByLabelText("What should this skill do?"), { target: { value: "Run safely" } }); const button = screen.getByRole("button", { name: "Confirm & Run" }); fireEvent.click(button); fireEvent.click(button);
    await waitFor(() => expect(confirm).toHaveBeenCalledOnce()); expect(confirm).toHaveBeenCalledWith("Run safely");
  });
});
