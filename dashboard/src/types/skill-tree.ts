export type NodeStatus = "available" | "running" | "completed" | "waiting-for-approval" | "failed" | "not-configured";

export type Department = {
  id: string;
  name: string;
  shortLabel: string;
  color: string;
  description: string;
};

export type Skill = {
  id: string;
  name: string;
  departmentId: string;
  description: string;
  status: NodeStatus;
  autonomy: "Assisted" | "Supervised" | "Autonomous";
  tools: string[];
  dependencies: string[];
  outputs: string[];
  lastRun: string;
  metrics: { label: string; value: string }[];
};

export type ActivityEvent = {
  id: string;
  title: string;
  detail: string;
  time: string;
  status: NodeStatus;
  departmentId: string;
};

export type AxionNodeData = {
  label: string;
  kind: "brain" | "department" | "skill";
  color: string;
  status?: NodeStatus;
  departmentId?: string;
  skillId?: string;
};
