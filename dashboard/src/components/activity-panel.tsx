import { motion } from "framer-motion";
import { Activity, ArrowUpRight } from "lucide-react";
import type { ActivityEvent } from "@/types/skill-tree";
import { statusTone } from "@/lib/status";

export function ActivityPanel({ events, expanded = false }: { events: ActivityEvent[]; expanded?: boolean }) {
  return <motion.aside className={expanded ? "activity-panel expanded" : "activity-panel"} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}><div className="panel-heading"><div><Activity size={15} /><span>LIVE ACTIVITY</span></div><button aria-label="Open full activity"><ArrowUpRight size={15} /></button></div>{events.length === 0 ? <div className="empty-state">No activity yet. Skill runs will appear here.</div> : <div className="activity-list">{events.map((event) => <article key={event.id}><span className="event-line" style={{ background: statusTone(event.status) }} /><div><strong>{event.title}</strong><p>{event.detail}</p></div><time>{event.time}</time></article>)}</div>}</motion.aside>;
}
