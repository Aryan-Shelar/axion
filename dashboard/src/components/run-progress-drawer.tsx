"use client";
import { useEffect, useRef, useState } from "react";
import type { HermesApprovalDecision, HermesRunEvent, HermesRunSummary } from "@/lib/hermes/types";

const labels: Record<HermesRunSummary["status"], string> = { starting: "Starting", queued: "Queued", running: "Running", waiting_for_approval: "Waiting for approval", stopping: "Stopping", completed: "Completed", failed: "Failed", cancelled: "Cancelled", disconnected: "Disconnected", unknown: "Unknown" };
const terminal = new Set(["completed", "failed", "cancelled"]);
type Props = { run: HermesRunSummary; skillName: string; createdAt: number; timeline: HermesRunEvent[]; output: string; error: string | null; liveAvailable: boolean; connected: boolean; canStop: boolean; canApprove: boolean; stopping: boolean; approving: boolean; opener?: HTMLElement | null; onRefresh: () => void; onApprove: (decision: HermesApprovalDecision) => void; onStop: () => void; onClose: () => void };
export function RunProgressDrawer(props: Props) {
  const [confirmStop, setConfirmStop] = useState(false); const close = useRef<HTMLButtonElement>(null); const isTerminal = terminal.has(props.run.status);
  useEffect(() => { close.current?.focus(); return () => { if (props.opener?.isConnected) props.opener.focus(); }; }, [props.opener]);
  const requestClose = () => { if (!isTerminal && !window.confirm("This run will keep running. Close the live run drawer?")) return; props.onClose(); };
  return <><button className="drawer-scrim run-drawer-scrim" aria-label="Close run drawer backdrop" onClick={requestClose} /><aside className="skill-drawer run-progress-drawer" role="dialog" aria-modal="true" aria-label={`${props.skillName} run progress`}>
    <header><span>Hermes / Live run</span><h2>{props.skillName}</h2><p className="run-id">{props.run.runId}</p><strong className={`run-state ${props.run.status}`}>{labels[props.run.status]}</strong></header>
    <div className="drawer-content"><section><h3>Status</h3><p>{labels[props.run.status]} · elapsed {Math.max(0, Math.floor((Date.now() - props.createdAt) / 1000))}s</p>{!props.liveAvailable && <p className="run-notice">Live updates unavailable</p>}{props.liveAvailable && !props.connected && <p className="run-notice">Disconnected. Reconnecting…</p>}<button onClick={props.onRefresh}>Refresh status</button></section>
    {props.run.approval && <section className="approval-card"><h3>{props.run.approval.title}</h3><p>{props.run.approval.summary}</p>{props.canApprove ? <div><button disabled={props.approving} onClick={() => props.onApprove("once")}>Approve once</button><button disabled={props.approving} onClick={() => props.onApprove("deny")}>Deny</button></div> : <p>Connected Hermes cannot resolve this approval request from AXION. You may stop the run if stopping is supported.</p>}</section>}
    <section><h3>Progress</h3><ol className="run-timeline">{props.timeline.map((event, index) => <li key={index}>{event.type === "status" ? labels[event.status] : event.type === "tool" || event.type === "progress" ? event.label : event.type === "failure" ? event.message : event.type === "approval_required" ? event.approval.title : event.type === "approval_resolved" ? "Approval resolved" : "Hermes produced output"}</li>)}</ol></section>
    {props.output && <section><h3>Result</h3><pre className="run-output">{props.output}</pre></section>}{(props.error || props.run.error) && <section className="run-error"><h3>Run failed</h3><p>{props.error ?? props.run.error}</p></section>}
    </div><footer>{props.canStop && !isTerminal && !confirmStop && <button disabled={props.stopping} onClick={() => setConfirmStop(true)}>Stop Run</button>}{confirmStop && <div className="stop-confirm"><span>Stop this Hermes run?</span><button onClick={() => { props.onStop(); setConfirmStop(false); }}>Confirm Stop</button><button onClick={() => setConfirmStop(false)}>Keep Running</button></div>}{isTerminal && <button ref={close} onClick={props.onClose}>Close</button>}</footer>
  </aside></>;
}
