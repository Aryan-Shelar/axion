"use client";

import { useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Activity, Bot, Braces, Clock3, Gauge, History, Pencil, Play, Workflow, X } from "lucide-react";
import { departmentById } from "@/data/departments";
import type { Skill } from "@/types/skill-tree";
import type { HermesCapabilities, SkillInstallation } from "@/lib/hermes/types";
import { StatusBadge } from "./status-badge";

const installationLabels: Record<SkillInstallation, string> = { installed: "Installed in Hermes", prototype: "Prototype skill", unavailable: "Installation status unavailable" };

type Props = { skill: Skill | null; installation?: SkillInstallation; online?: boolean; capabilities?: HermesCapabilities | null; submitting?: boolean; onRunSkill?: (opener: HTMLButtonElement) => void; onClose: () => void };
export function SkillDetailDrawer({ skill, installation = "unavailable", online = false, capabilities = null, submitting = false, onRunSkill, onClose }: Props) {
  const [feedback, setFeedback] = useState("");
  const showFeedback = (action: string) => setFeedback(`${action} is a prototype action in this demo.`);
  const reason = !online ? "Hermes is offline" : installation === "prototype" ? "Prototype skills cannot run" : installation === "unavailable" ? "Installation status is unavailable" : !capabilities?.runSubmission ? "Connected Hermes does not support run submission" : submitting ? "A run is already starting" : null;

  return <AnimatePresence>{skill && <>
    <motion.button className="drawer-scrim" aria-label="Close skill details" onClick={onClose} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
    <motion.aside className="skill-drawer" aria-label={`${skill.name} details`} initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ type: "spring", stiffness: 330, damping: 34 }}>
      <header>
        <div className="drawer-symbol" style={{ color: departmentById[skill.departmentId].color }}><Braces size={24} /></div>
        <button onClick={onClose} aria-label="Close details"><X size={18} /></button>
        <span>{departmentById[skill.departmentId].name} / Skill</span><h2>{skill.name}</h2><p>{skill.description}</p>
        <div className="drawer-badges"><StatusBadge status={skill.status} /><span><Gauge size={13} />{skill.autonomy}</span></div>
        <div className={`skill-installation ${installation}`}>{installationLabels[installation]}</div>
      </header>
      <div className="drawer-content">
        <section><h3><Bot size={14} />Tools</h3><div className="chips">{skill.tools.map((tool) => <span key={tool}>{tool}</span>)}</div></section>
        <div className="detail-grid">
          <section><h3><Workflow size={14} />Dependencies</h3>{skill.dependencies.map((item) => <p key={item}>{item}</p>)}</section>
          <section><h3><Activity size={14} />Outputs</h3>{skill.outputs.map((item) => <p key={item}>{item}</p>)}</section>
        </div>
        <section><h3><Clock3 size={14} />Last run</h3><p className="last-run">{skill.lastRun}</p></section>
        <section><h3>Performance / 7 days · Demo data</h3><div className="metric-grid">{skill.metrics.map((metric) => <div key={metric.label}><strong>{metric.value}</strong><span>{metric.label}</span></div>)}</div></section>
      </div>
      {feedback && <motion.div className="action-feedback" role="status" initial={{ opacity: 0, y: 5 }} animate={{ opacity: 1, y: 0 }}>{feedback}</motion.div>}
      <footer>
        <div className="run-skill-action"><button className="phase-b-button" disabled={Boolean(reason)} onClick={(event) => onRunSkill?.(event.currentTarget)}><Play size={16} />Run Skill</button>{reason && <small>{reason}</small>}</div>
        <button onClick={() => showFeedback("Edit")}><Pencil size={15} />Edit</button>
        <button onClick={() => showFeedback("History")}><History size={15} />History</button>
      </footer>
    </motion.aside>
  </>}</AnimatePresence>;
}
