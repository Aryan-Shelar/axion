import type { NodeStatus } from "@/types/skill-tree";
import { formatStatus, statusTone } from "@/lib/status";

export function StatusBadge({ status, compact = false }: { status: NodeStatus; compact?: boolean }) {
  const color = statusTone(status);
  return (
    <span className="status-badge" style={{ color, borderColor: `${color}45`, background: `${color}12` }}>
      <span className={status === "running" ? "status-dot pulse" : "status-dot"} style={{ background: color }} />
      {!compact && formatStatus(status)}
    </span>
  );
}
