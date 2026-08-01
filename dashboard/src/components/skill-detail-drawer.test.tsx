import React from "react";
import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import { skills } from "@/data/skills";
import { SkillDetailDrawer } from "./skill-detail-drawer";

describe("SkillDetailDrawer", () => {
  it.each(["Edit", "History"])("shows visible prototype feedback for %s", (action) => {
    render(<SkillDetailDrawer skill={skills[0]} installation="prototype" onClose={() => undefined} />);
    fireEvent.click(screen.getByRole("button", { name: action }));
    expect(screen.getByRole("status")).toHaveTextContent(new RegExp(action.replace(" Skill", ""), "i"));
    expect(screen.getByRole("status")).toHaveTextContent(/prototype/i);
  });

  it.each([["installed", "Installed in Hermes"], ["prototype", "Prototype skill"], ["unavailable", "Installation status unavailable"]] as const)("renders %s installation state", (installation, label) => {
    render(<SkillDetailDrawer skill={skills[0]} installation={installation} onClose={() => undefined} />);
    expect(screen.getByText(label)).toBeInTheDocument();
  });

  it("enables execution only for an online installed skill with submission support", () => {
    render(<SkillDetailDrawer skill={skills[0]} installation="installed" online capabilities={{ runSubmission: true, runStatus: true, runEventsSse: true, runStop: true, runApprovalResponse: true, approvalEvents: true }} onClose={() => undefined} onRunSkill={() => undefined} />);
    expect(screen.getByRole("button", { name: "Run Skill" })).toBeEnabled();
  });

  it.each([["prototype", true, "Prototype skills cannot run"], ["unavailable", true, "Installation status is unavailable"], ["installed", false, "Hermes is offline"]] as const)("disables %s when online=%s", (installation, online, reason) => {
    render(<SkillDetailDrawer skill={skills[0]} installation={installation} online={online} capabilities={{ runSubmission: true, runStatus: true, runEventsSse: true, runStop: true, runApprovalResponse: true, approvalEvents: true }} onClose={() => undefined} />);
    expect(screen.getByRole("button", { name: "Run Skill" })).toBeDisabled(); expect(screen.getByText(reason)).toBeInTheDocument();
  });
});
