import { motion } from "framer-motion";
import { Activity, ArrowUpRight, RefreshCw } from "lucide-react";
import type { KeyboardEvent } from "react";
import type { HermesPublicError, HermesSessionSummary } from "@/lib/hermes/types";
import { formatSessionUpdatedAt, sessionSecondaryText, sortSessionsNewestFirst } from "@/lib/hermes/session-activity";

type Props = {
  sessions: HermesSessionSummary[] | null;
  loading: boolean;
  error: HermesPublicError | null;
  expanded?: boolean;
  onSelectSession: (session: HermesSessionSummary, opener: HTMLButtonElement) => void;
  onRefresh: () => void;
  onOpenFull?: () => void;
};

export function ActivityPanel({ sessions, loading, error, expanded = false, onSelectSession, onRefresh, onOpenFull }: Props) {
  const sorted = sortSessionsNewestFirst(sessions ?? []);
  const visible = expanded ? sorted : sorted.slice(0, 3);
  const openFromKeyboard = (event: KeyboardEvent<HTMLButtonElement>, session: HermesSessionSummary) => {
    if (event.key === "Enter" || event.key === " ") { event.preventDefault(); onSelectSession(session, event.currentTarget); }
  };
  return <motion.aside className={expanded ? "activity-panel expanded" : "activity-panel"} initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}>
    <div className="panel-heading"><div><Activity size={15} /><span>HERMES ACTIVITY</span></div>{expanded
      ? <button onClick={onRefresh} aria-label="Refresh Hermes activity"><RefreshCw size={15} />Refresh</button>
      : <button onClick={onOpenFull} aria-label="Open full activity"><ArrowUpRight size={15} /></button>}</div>
    {error && sessions !== null && <div className={`activity-warning ${error.code}`} role="status">{error.message}</div>}
    {loading && sessions === null ? <div className="activity-state">Loading Hermes activity…</div>
      : error && sessions === null ? <div className={`activity-state unavailable ${error.code}`} role="alert">{error.message}</div>
      : visible.length === 0 ? <div className="empty-state">No Hermes activity yet.</div>
      : <div className="activity-list">{visible.map((session) => {
        const secondary = sessionSecondaryText(session); const updated = formatSessionUpdatedAt(session.updatedAt);
        return <button className="session-row" key={session.id} aria-label={`Open ${session.title}`} onClick={(event) => onSelectSession(session, event.currentTarget)} onKeyDown={(event) => openFromKeyboard(event, session)}>
          <span className="event-line" /><div><strong>{session.title}</strong>{secondary && <p>{secondary}</p>}</div>{updated && <time dateTime={session.updatedAt}>{updated}</time>}
        </button>;
      })}</div>}
  </motion.aside>;
}
