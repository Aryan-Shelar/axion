"use client";

import { useEffect, useId, useRef } from "react";
import { AnimatePresence, motion } from "framer-motion";
import { Clock3, X } from "lucide-react";
import type { HermesSessionSummary } from "@/lib/hermes/types";
import { formatSessionUpdatedAt } from "@/lib/hermes/session-activity";

type SessionDetailDrawerProps = {
  session: HermesSessionSummary | null;
  opener: HTMLElement | null;
  onClose: () => void;
};

export function SessionDetailDrawer({ session, opener, onClose }: SessionDetailDrawerProps) {
  const titleId = useId();
  const dialogRef = useRef<HTMLElement>(null);
  const closeRef = useRef<HTMLButtonElement>(null);

  useEffect(() => {
    if (!session) return;
    closeRef.current?.focus();

    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        event.preventDefault();
        onClose();
        return;
      }
      if (event.key !== "Tab") return;

      const focusable = Array.from(dialogRef.current?.querySelectorAll<HTMLElement>(
        'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])',
      ) ?? []);
      if (focusable.length === 0) {
        event.preventDefault();
        dialogRef.current?.focus();
        return;
      }

      const first = focusable[0];
      const last = focusable[focusable.length - 1];
      if (focusable.length === 1 || (event.shiftKey && document.activeElement === first) || (!event.shiftKey && document.activeElement === last)) {
        event.preventDefault();
        (event.shiftKey ? last : first).focus();
      }
    };

    document.addEventListener("keydown", handleKeyDown);
    return () => {
      document.removeEventListener("keydown", handleKeyDown);
      if (opener?.isConnected) opener.focus();
    };
  }, [onClose, opener, session]);

  const updatedAt = formatSessionUpdatedAt(session?.updatedAt);

  return <AnimatePresence>{session && <>
    <motion.button className="drawer-scrim session-drawer-scrim" aria-label="Close session drawer backdrop" onClick={onClose} initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} />
    <motion.aside ref={dialogRef} className="skill-drawer session-drawer" role="dialog" aria-modal="true" aria-label={`${session.title} details`} tabIndex={-1} initial={{ x: "100%" }} animate={{ x: 0 }} exit={{ x: "100%" }} transition={{ type: "spring", stiffness: 330, damping: 34 }}>
      <header>
        <div className="drawer-symbol"><Clock3 size={24} /></div>
        <button ref={closeRef} onClick={onClose} aria-label="Close session details"><X size={18} /></button>
        <span>Hermes / Session</span>
        <h2 id={titleId}>{session.title}</h2>
        <p>Read-only session metadata</p>
      </header>
      <div className="drawer-content session-detail-list">
        <section><h3>Session ID</h3><p>{session.id}</p></section>
        <section><h3>Source</h3><p>{session.source ?? "Not available"}</p></section>
        <section><h3>Status</h3><p>{session.status ?? "Not available"}</p></section>
        <section><h3>Last updated</h3><p>{updatedAt ?? "Not available"}</p></section>
      </div>
    </motion.aside>
  </>}</AnimatePresence>;
}
