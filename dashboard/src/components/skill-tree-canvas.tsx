"use client";

import { useMemo, useState } from "react";
import { Background, BackgroundVariant, MiniMap, ReactFlow, ReactFlowProvider, useReactFlow, type NodeMouseHandler } from "@xyflow/react";
import { Focus, Map as MapIcon, Minus, Plus } from "lucide-react";
import "@xyflow/react/dist/style.css";
import { skillEdges, skillNodes } from "@/data/graph";
import { BrainNode } from "./nodes/brain-node";
import { DepartmentNode } from "./nodes/department-node";
import { SkillNode } from "./nodes/skill-node";
import { BackgroundAtmosphere } from "./background-atmosphere";

const nodeTypes = { brain: BrainNode, department: DepartmentNode, skill: SkillNode };

function CanvasControls({ minimap, onToggleMinimap }: { minimap: boolean; onToggleMinimap: () => void }) {
  const { zoomIn, zoomOut, fitView } = useReactFlow();
  return <div className="map-controls" role="group" aria-label="Map controls"><button onClick={() => zoomIn()} aria-label="Zoom in"><Plus size={17} /></button><button onClick={() => zoomOut()} aria-label="Zoom out"><Minus size={17} /></button><button onClick={() => fitView({ padding: 0.15, duration: 700 })} aria-label="Fit map to view"><Focus size={17} /></button><button className={minimap ? "enabled" : ""} onClick={onToggleMinimap} aria-label="Toggle mini-map" aria-pressed={minimap}><MapIcon size={17} /></button></div>;
}

function Canvas({ query, onSelectSkill }: { query: string; onSelectSkill: (id: string) => void }) {
  const [minimap, setMinimap] = useState(true);
  const nodes = useMemo(() => {
    const normalized = query.trim().toLowerCase();
    return skillNodes.map((node) => {
      const matches = normalized && node.data.label.toLowerCase().includes(normalized);
      return { ...node, className: normalized ? (matches ? "matched-node" : "dimmed-node") : "" };
    });
  }, [query]);
  const handleNodeClick: NodeMouseHandler = (_, node) => { if (node.data.kind === "skill" && typeof node.data.skillId === "string") onSelectSkill(node.data.skillId); };

  return <div className="skilltree-wrap"><BackgroundAtmosphere /><ReactFlow nodes={nodes} edges={skillEdges} nodeTypes={nodeTypes} onNodeClick={handleNodeClick} fitView fitViewOptions={{ padding: 0.06 }} minZoom={0.25} maxZoom={1.5} defaultEdgeOptions={{ selectable: false }} nodesConnectable={false} nodesDraggable={false} proOptions={{ hideAttribution: true }}><Background variant={BackgroundVariant.Dots} gap={28} size={1} color="rgba(91, 137, 173, .22)" />{minimap && <MiniMap className="axion-minimap" pannable zoomable nodeColor={(node) => String(node.data.color || "#22d3ee")} maskColor="rgba(3, 8, 18, .78)" />}<CanvasControls minimap={minimap} onToggleMinimap={() => setMinimap((value) => !value)} /></ReactFlow><div className="canvas-meta"><span>DEMO TOPOLOGY</span><strong>49 prototype connections</strong></div></div>;
}

export function SkillTreeCanvas(props: { query: string; onSelectSkill: (id: string) => void }) {
  return <ReactFlowProvider><Canvas {...props} /></ReactFlowProvider>;
}
