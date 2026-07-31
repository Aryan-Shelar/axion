import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { Boxes } from "lucide-react";
import type { AxionNodeData } from "@/types/skill-tree";

export function DepartmentNode({ data }: NodeProps<Node<AxionNodeData>>) {
  return <div className="department-node" style={{ "--node-color": data.color } as React.CSSProperties}><Handle type="target" position={Position.Top} className="invisible-handle" /><div className="department-icon"><Boxes size={18} /></div><div><span>DEPARTMENT</span><strong>{data.label}</strong></div><i>{data.departmentId === "customer" ? "05" : data.departmentId === "intelligence" ? "07" : "06"} SKILLS</i><Handle type="source" position={Position.Bottom} className="invisible-handle" /></div>;
}
