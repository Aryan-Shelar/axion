import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { CircleDotDashed } from "lucide-react";
import { StatusBadge } from "@/components/status-badge";
import type { AxionNodeData } from "@/types/skill-tree";

export function SkillNode({ data, selected }: NodeProps<Node<AxionNodeData>>) {
  const installationLabel = data.installation === "installed" ? "Installed in Hermes" : data.installation === "unavailable" ? "Installation status unavailable" : "Prototype skill";
  return <div className={selected ? "skill-node selected" : "skill-node"} style={{ "--node-color": data.color } as React.CSSProperties} title={installationLabel}><Handle type="target" position={Position.Top} className="invisible-handle" /><CircleDotDashed size={14} /><span>{data.label}</span><i className={`installation-dot ${data.installation ?? "prototype"}`} aria-label={installationLabel} />{data.status && <StatusBadge status={data.status} compact />}</div>;
}
