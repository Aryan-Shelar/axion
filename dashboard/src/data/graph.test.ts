import { describe, expect, it } from "vitest";
import { departments } from "./departments";
import { skills } from "./skills";
import { skillEdges, skillNodes } from "./graph";

describe("AXION skill graph", () => {
  it("contains the seven requested departments", () => expect(departments).toHaveLength(7));
  it("contains all 42 initial specialist skills", () => expect(skills).toHaveLength(42));
  it("centers the brain and links every department and skill", () => {
    expect(skillNodes.find((node) => node.id === "brain")?.position).toEqual({ x: 0, y: 0 });
    expect(skillEdges).toHaveLength(departments.length + skills.length);
    expect(skillEdges.every((edge) => skillNodes.some((node) => node.id === edge.source))).toBe(true);
    expect(skillEdges.every((edge) => skillNodes.some((node) => node.id === edge.target))).toBe(true);
  });
});
