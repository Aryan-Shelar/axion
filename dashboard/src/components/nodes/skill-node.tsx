import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { CircleDotDashed } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";
import type { AxionNodeData } from "@/types/skill-tree";

export function SkillNode({ data, selected }: NodeProps<Node<AxionNodeData>>) {
  return <div className={selected ? "skill-node selected" : "skill-node"} style={{ "--node-color": data.color } as React.CSSProperties}><Handle type="target" position={Position.Top} className="invisible-handle" /><CircleDotDashed size={14} /><span>{data.label}</span>{data.status && <StatusBadge status={data.status} compact />}</div>;
}
