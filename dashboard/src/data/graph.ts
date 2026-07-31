import type { Edge, Node } from "@xyflow/react";
import { departments, departmentById } from "./departments";
import { skills } from "./skills";
import type { AxionNodeData } from "@/types/skill-tree";

const CENTER = { x: 0, y: 0 };
const HUB_RADIUS_X = 690;
const HUB_RADIUS_Y = 430;

export const skillNodes: Node<AxionNodeData>[] = [
  { id: "brain", type: "brain", position: CENTER, data: { label: "AXION Brain", kind: "brain", color: "#22D3EE" }, draggable: false },
];

departments.forEach((department, departmentIndex) => {
  const angle = -Math.PI / 2 + (departmentIndex * Math.PI * 2) / departments.length;
  const hub = { x: Math.cos(angle) * HUB_RADIUS_X, y: Math.sin(angle) * HUB_RADIUS_Y };
  skillNodes.push({
    id: `department-${department.id}`,
    type: "department",
    position: hub,
    data: { label: department.name, kind: "department", color: department.color, departmentId: department.id },
    draggable: false,
  });

  const members = skills.filter((skill) => skill.departmentId === department.id);
  members.forEach((skill, skillIndex) => {
    const spread = members.length > 1 ? (skillIndex / (members.length - 1) - 0.5) * 1.45 : 0;
    const skillAngle = angle + spread;
    const distance = 230 + (skillIndex % 2) * 42;
    skillNodes.push({
      id: `skill-${skill.id}`,
      type: "skill",
      position: { x: hub.x + Math.cos(skillAngle) * distance, y: hub.y + Math.sin(skillAngle) * distance },
      data: { label: skill.name, kind: "skill", color: department.color, status: skill.status, departmentId: department.id, skillId: skill.id },
      draggable: false,
    });
  });
});

export const skillEdges: Edge[] = [
  ...departments.map((department) => ({
    id: `brain-${department.id}`,
    source: "brain",
    target: `department-${department.id}`,
    type: "smoothstep",
    animated: true,
    style: { stroke: department.color, strokeWidth: 1.7, opacity: 0.58 },
  })),
  ...skills.map((skill) => ({
    id: `${skill.departmentId}-${skill.id}`,
    source: `department-${skill.departmentId}`,
    target: `skill-${skill.id}`,
    type: "bezier",
    animated: skill.status === "running",
    style: { stroke: departmentById[skill.departmentId].color, strokeWidth: 1, opacity: 0.32 },
  })),
];
