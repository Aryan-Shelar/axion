import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { skills } from "@/data/skills";
import { SkillDetailDrawer } from "./skill-detail-drawer";

describe("SkillDetailDrawer", () => {
  it.each(["Run Skill", "Edit", "History"])("shows visible prototype feedback for %s", (action) => {
    render(<SkillDetailDrawer skill={skills[0]} onClose={() => undefined} />);
    fireEvent.click(screen.getByRole("button", { name: action }));
    expect(screen.getByRole("status")).toHaveTextContent(new RegExp(action.replace(" Skill", ""), "i"));
    expect(screen.getByRole("status")).toHaveTextContent(/prototype/i);
  });
});
