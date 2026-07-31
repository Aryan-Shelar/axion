import type { NodeStatus } from "@/types/skill-tree";

const labels: Record<NodeStatus, string> = {
  available: "Available",
  running: "Running",
  completed: "Completed",
  "waiting-for-approval": "Waiting for approval",
  failed: "Failed",
  "not-configured": "Not configured",
};

export const formatStatus = (status: NodeStatus) => labels[status];

export const statusTone = (status: NodeStatus) => ({
  available: "#22d3ee",
  running: "#60a5fa",
  completed: "#34d399",
  "waiting-for-approval": "#fbbf24",
  failed: "#fb7185",
  "not-configured": "#64748b",
})[status];
