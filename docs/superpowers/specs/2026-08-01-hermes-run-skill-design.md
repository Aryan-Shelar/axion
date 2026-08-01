# Secure Hermes Skill Execution Design

Approved by the repository owner on 2026-08-01 through the Phase B implementation brief. This design extends the Phase A read-only Hermes bridge without weakening its GET-only client.

## Goal and scope

AXION will run a small trusted set of installed Hermes skills from the dashboard through a server-only bridge. A user supplies one task, explicitly confirms it, observes bounded live progress, resolves sensitive actions with only **Approve once** or **Deny**, can request a safe stop, and can recover an active run after refresh. Scheduled work, model/provider selection, session editing, message editing, arbitrary tools, and generic proxying remain out of scope.

## Architecture

The only execution path is `Browser -> focused AXION /api/hermes routes -> Hermes`. Browser code never contacts port 8642 and never receives `HERMES_API_KEY`. The existing `hermesGet` client stays read-only. A new `run-client.ts`, marked `server-only`, implements only the seven fixed operations required for capabilities, installed skills, run creation/status/events/approval/stop. Run IDs must match `^[A-Za-z0-9_-]{1,128}$` before interpolation.

Capability normalization feature-detects `run_submission`, `run_status`, `run_events_sse`, `run_stop`, `run_approval_response` (and the legacy/equivalent `run_approval`), and `approval_events`. Submission is enabled only when Hermes is online, the AXION ID is in `HERMES_SKILL_ALIASES`, the current normalized `/v1/skills` response contains the same ID, submission is supported, and no local submission is starting.

## Server trust boundary

All write routes require JSON content type, reject a present cross-origin `Origin`, reject malformed bodies and unknown fields, and return normalized envelopes and public errors. Run creation accepts exactly `skillId`, trimmed `task` (3–4000 characters), and a UUID `idempotencyKey`. The browser cannot send instructions, sessions, paths, commands, provider, model, tools, toolsets, or Hermes options.

The server re-fetches capabilities and installed skills. It constructs the documented Hermes run payload using only `input`, controlled `instructions`, and a generated `session_id`. The instruction names the selected installed skill as the primary workflow and requires truthful completion reporting. The idempotency key is forwarded as `Idempotency-Key`; AXION also maintains a short-lived in-process pending/completed registry so concurrent duplicate submissions share or reject one upstream creation rather than starting two runs.

Upstream authentication, offline, timeout, malformed JSON, and HTTP errors are classified. No raw upstream body, headers, exception detail, stack, or secret crosses the route boundary.

## Normalized run model

Public run states are `starting`, `queued`, `running`, `waiting_for_approval`, `stopping`, `completed`, `failed`, `cancelled`, `disconnected`, and `unknown`. Status responses expose only run ID, state, bounded output (50,000 characters), safe error text, timestamps when scalar and valid, and a normalized pending approval when present.

SSE is primary when available. The AXION events route opens Hermes `/events` with bearer authentication, forwards client cancellation, parses event frames incrementally, and emits sanitized AXION events without buffering the whole response. Known lifecycle, text delta/final output, tool start/complete, approval request/response, and safe failure shapes normalize to a small public union. Unknown events become a generic progress event or are ignored. Tool arguments/results, command output, headers, environment data, and unrestricted payloads are never relayed. Event labels are capped, approval summaries are capped at 1,000 characters, output is capped at 50,000 characters, and the browser retains at most 200 timeline entries.

Current Hermes upstream evidence (NousResearch `gateway/platforms/api_server.py`, inspected 2026-08-01) advertises `run_approval_response` plus `approval_events`, emits `approval.request`, and resolves a run with `{ "choice": "once" }` or `{ "choice": "deny" }`. AXION translates its public `{ "decision": "once" | "deny" }` into that exact body and rejects all other decisions. It never exposes Hermes' `session` or `always` choices.

## Browser state and UI

`useHermesDashboard()` adds the normalized capabilities resource. `SkillDetailDrawer` receives connectivity, capabilities, and a submission-in-progress signal and renders an enabled **Run Skill** only for a trusted installed executable skill; otherwise it gives one accurate disabled reason.

`RunSkillDialog` is a focused accessible modal above the skill drawer. It contains the exact label **What should this skill do?**, a character counter, Cancel, and **Confirm & Run**. Focus starts in the textarea; Escape/backdrop close only before submission; validation and an in-flight guard prevent duplicates; the underlying skill drawer remains open until creation succeeds.

`useHermesRun` owns creation, initial reconciliation, SSE connection and capped reconnect backoff, polling fallback, approval, stopping, recovery storage, and cleanup. `RunProgressDrawer` is presentational: semantic status, elapsed time, capped timeline/output, safe errors, optional approval card, optional Stop Run, manual refresh, and terminal Close. Active close requires confirmation and never stops the run implicitly. Focus is trapped and restored to the Run Skill opener.

When SSE is unsupported but submission and status are supported, execution uses status polling and clearly shows **Live updates unavailable**. When approval support is absent, no approval buttons appear and the drawer explains that AXION cannot resolve the request; Stop remains available when supported. Stop moves to `stopping` and remains there until status/event reconciliation confirms `cancelled`.

## Refresh recovery

Browser storage contains only `runId`, `skillId`, `skillName`, and `createdAt`. On load, AXION validates the run ID, fetches normalized status, reopens active work and reconnects, may display a terminal result once, and clears missing/expired data. Task text, output, approval data/tokens, raw tool data, credentials, and secrets are never persisted. Recovery never starts a new run.

## Testing and verification

Development follows red-green-refactor. Pure normalizers and validators receive unit tests; route tests mock upstream fetches and assert trust-boundary behavior, streaming, abort propagation, bounded output, and safe errors; component/hook tests cover enablement, dialog validation/deduplication, live states, approvals, stopping, reconnect, and storage. Existing dashboard, map, activity, skill/session drawers, search, and status tests remain regression coverage.

Final automated verification is `npm test`, `npm run lint`, and `npm run build` from `dashboard`. A local manual integration is attempted only against a safely available Hermes gateway and uses harmless tasks; lack of an installed/running local Hermes is reported rather than simulated.

## Security invariants

- `HERMES_API_KEY` is referenced only by server-only clients and never by browser modules.
- No route accepts an upstream URL, arbitrary method/path, arbitrary skill, or arbitrary agent options.
- Only IDs trusted by AXION and concurrently reported installed by Hermes may run.
- Only `once` and `deny` decisions are accepted.
- Task, run ID, output, timeline, and approval summary sizes are bounded.
- Existing Phase A GET routes and their client remain read-only.
- Errors and SSE events are allowlist-normalized before reaching JavaScript.
