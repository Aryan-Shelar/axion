import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";
import { BrainCircuit } from "lucide-react";
import type { AxionNodeData } from "@/types/skill-tree";

export function BrainNode({ data }: NodeProps<Node<AxionNodeData>>) {
  return <div className="brain-node"><Handle type="source" position={Position.Top} className="invisible-handle" /><div className="brain-orbit orbit-one" /><div className="brain-orbit orbit-two" /><div className="brain-core"><BrainCircuit size={33} /><strong>{data.label}</strong><span>ORCHESTRATION CORE</span></div></div>;
}
