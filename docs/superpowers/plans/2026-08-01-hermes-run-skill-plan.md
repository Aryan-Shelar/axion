# Secure Hermes Skill Execution Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Securely execute trusted, currently installed Hermes skills from AXION with explicit confirmation, safe live progress, approvals, stopping, and refresh recovery.

**Architecture:** Keep the Phase A GET-only client unchanged and add a separate server-only execution client with fixed operations. Focused Next.js routes validate browser input and normalize all Hermes data; a dedicated hook owns run transport/recovery while small modal components render confirmation and progress.

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript 5.7, Vitest, Testing Library, native Fetch/ReadableStream/EventSource APIs.

## Global Constraints

- Browser requests only AXION `/api/hermes/*`; `HERMES_API_KEY` stays server-only.
- Run IDs match `^[A-Za-z0-9_-]{1,128}$`; tasks trim to 3–4000 characters.
- Only IDs in `HERMES_SKILL_ALIASES` and the current normalized Hermes `/v1/skills` response can run.
- Browser run creation accepts exactly `skillId`, `task`, and UUID `idempotencyKey`.
- Browser approval accepts only `decision: "once" | "deny"`; upstream body is `{ choice: decision }`.
- SSE is primary; polling is recovery/fallback/reconciliation only.
- At most 200 timeline events, 50,000 output characters, and 1,000 approval-summary characters.
- Existing read-only client/routes remain read-only; no generic proxy is introduced.
- Do not stage `data/organizer/` or the unrelated 2026-07-30 untracked documents.

---

### Task 1: Public capability, run, and event contracts

**Files:**
- Modify: `dashboard/src/lib/hermes/types.ts`
- Create: `dashboard/src/lib/hermes/run-normalize.ts`
- Create: `dashboard/src/lib/hermes/run-normalize.test.ts`
- Modify: `dashboard/src/hooks/use-hermes-dashboard.ts`

**Interfaces:**
- Produces `HermesCapabilities`, `HermesRunStatus`, `HermesRunSummary`, `HermesRunEvent`, `HermesApprovalRequest`, `HermesApprovalDecision`, `normalizeCapabilities`, `normalizeRunSummary`, `normalizeRunEvent`, `isValidRunId`, and exported size limits.

- [ ] Write failing tests for feature aliases, all public statuses, bounded output/approval text, known lifecycle/tool/text/approval events, unknown events, and run-ID validation.
- [ ] Run `npm test -- src/lib/hermes/run-normalize.test.ts` and confirm failures are caused by missing exports.
- [ ] Implement the minimal pure types/normalizers; add `/api/hermes/capabilities` to `useHermesDashboard()` with a 60-second refresh.
- [ ] Re-run the focused tests and existing Hermes normalizer/hook tests.
- [ ] Commit only these files as `feat: add normalized Hermes run capabilities and types`.

### Task 2: Restricted server-only execution client

**Files:**
- Create: `dashboard/src/lib/hermes/run-client.ts`
- Create: `dashboard/src/lib/hermes/run-client.test.ts`

**Interfaces:**
- Produces fixed functions `getRunCapabilities`, `getInstalledRunSkills`, `createHermesRun`, `getHermesRun`, `openHermesRunEvents`, `respondHermesApproval`, and `stopHermesRun`; each accepts only typed arguments plus optional `{ signal, fetchImpl }` test injection.

- [ ] Write failing tests proving fixed method/path selection, bearer auth, `cache: "no-store"`, abort/timeout handling, JSON classification, run-ID rejection, idempotency forwarding, and SSE body passthrough.
- [ ] Run the focused test and confirm missing-module failures.
- [ ] Implement a `server-only` client with fixed URL construction and no browser-controlled path/method.
- [ ] Re-run focused tests and `dashboard/src/lib/hermes/client.test.ts` to prove the read-only client is unchanged.
- [ ] Commit as `feat: add restricted server-side Hermes run client`.

### Task 3: Request validation and focused API routes

**Files:**
- Create: `dashboard/src/lib/hermes/run-route.ts`
- Create: `dashboard/src/lib/hermes/run-route.test.ts`
- Create: `dashboard/src/app/api/hermes/capabilities/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/[runId]/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/[runId]/approval/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/[runId]/stop/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/run-routes.test.ts`

**Interfaces:**
- `validateJsonWrite(request, allowedFields)` enforces content type/origin/object/unknown-field rules.
- `parseCreateRunRequest` returns `{ skillId, task, idempotencyKey }`; `parseApprovalRequest` returns the two-choice decision.
- Routes return only normalized `HermesEnvelope<T>` data and public errors.

- [ ] Write failing tests for malformed JSON, content type, cross-origin, unknown fields, UUID/task bounds, arbitrary option rejection, trusted/install checks, normalized creation/status/approval/stop, duplicate idempotency, and secret absence.
- [ ] Run the focused route tests and confirm expected failures.
- [ ] Implement validators, a bounded in-process idempotency registry, server-generated instructions/session ID, current capability/skill checks, and focused handlers.
- [ ] Re-run focused and existing route tests.
- [ ] Commit as `feat: add validated Hermes run API routes`.

### Task 4: Sanitized streaming bridge

**Files:**
- Create: `dashboard/src/lib/hermes/sse.ts`
- Create: `dashboard/src/lib/hermes/sse.test.ts`
- Create: `dashboard/src/app/api/hermes/runs/[runId]/events/route.ts`
- Create: `dashboard/src/app/api/hermes/runs/[runId]/events/route.test.ts`

**Interfaces:**
- `createSanitizedSseStream(upstream, signal)` incrementally parses frames and emits only `HermesRunEvent` data frames.
- Events route returns `text/event-stream`, `no-cache`, `X-Accel-Buffering: no` and cancels upstream work on browser disconnect.

- [ ] Write failing tests for streaming-before-close, split frames, keepalives, known/unknown events, bounded fields, headers, invalid IDs, and downstream cancellation.
- [ ] Run focused tests and verify failures.
- [ ] Implement incremental TransformStream-style sanitization without whole-response buffering.
- [ ] Re-run focused tests.
- [ ] Commit as `feat: add sanitized Hermes run event bridge`.

### Task 5: Run confirmation dialog and skill enablement

**Files:**
- Create: `dashboard/src/components/run-skill-dialog.tsx`
- Create: `dashboard/src/components/run-skill-dialog.test.tsx`
- Modify: `dashboard/src/components/skill-detail-drawer.tsx`
- Modify: `dashboard/src/components/skill-detail-drawer.test.tsx`
- Modify: `dashboard/src/app/globals.css`

**Interfaces:**
- `RunSkillDialog` consumes skill identity, open/submitting/error state, `onCancel`, and async `onConfirm(task)`.
- `SkillDetailDrawer` consumes gateway/capability/submission state and `onRunSkill(opener)`.

- [ ] Write failing component tests for five enable/disable cases, accurate reasons, focus, exact label, 3/4000 validation, counter, Escape/backdrop, one submit under double click, and submitting lock.
- [ ] Run focused tests and verify failures.
- [ ] Implement accessible dialog semantics/focus trap and drawer button contract with no run side effects.
- [ ] Re-run focused tests.
- [ ] Commit as `feat: add run-skill confirmation dialog`.

### Task 6: Run hook, progress drawer, and polling fallback

**Files:**
- Create: `dashboard/src/hooks/use-hermes-run.ts`
- Create: `dashboard/src/hooks/use-hermes-run.test.tsx`
- Create: `dashboard/src/components/run-progress-drawer.tsx`
- Create: `dashboard/src/components/run-progress-drawer.test.tsx`
- Modify: `dashboard/src/app/globals.css`

**Interfaces:**
- `useHermesRun(capabilities)` exposes `run`, `timeline`, `output`, `createRun`, `refreshStatus`, `approve`, `stop`, `close`, submission flags, and transport state.
- `RunProgressDrawer` renders those values and emits presentational actions only.

- [ ] Write failing tests for creation, initial status reconciliation, healthy SSE, capped reconnect backoff, polling-only message, no continuous healthy polling, manual refresh, all state renderings, safe output/error, elapsed time, active-close warning, focus trap/restore, and timeline/output caps.
- [ ] Run focused tests and verify failures.
- [ ] Implement the minimal hook and drawer; use EventSource only for AXION URLs and stop transport on terminal state/unmount.
- [ ] Re-run focused tests.
- [ ] Commit as `feat: add live Hermes run drawer and stream hook`.

### Task 7: Approval and stop controls

**Files:**
- Modify: `dashboard/src/hooks/use-hermes-run.ts`
- Modify: `dashboard/src/hooks/use-hermes-run.test.tsx`
- Modify: `dashboard/src/components/run-progress-drawer.tsx`
- Modify: `dashboard/src/components/run-progress-drawer.test.tsx`

**Interfaces:**
- `approve("once" | "deny")` deduplicates in-flight decisions and reconciles status on failure/success.
- `stop()` enters `stopping`, deduplicates, and waits for terminal Hermes confirmation.

- [ ] Write failing tests that only two approval actions render, unsupported approval explains/no-auto-approve, duplicate decisions are blocked, stop confirmation is exact, duplicate stops are blocked, and `stopping` persists until reconciliation.
- [ ] Run focused tests and verify failures.
- [ ] Implement capability-gated controls and reconciliation.
- [ ] Re-run focused tests.
- [ ] Commit as `feat: add Hermes run approval and stop controls`.

### Task 8: Refresh recovery and page integration

**Files:**
- Modify: `dashboard/src/hooks/use-hermes-run.ts`
- Modify: `dashboard/src/hooks/use-hermes-run.test.tsx`
- Modify: `dashboard/src/app/page.tsx`
- Modify: `dashboard/src/app/page.test.tsx`

**Interfaces:**
- Storage key contains exactly `{ runId, skillId, skillName, createdAt }`.
- `Home` coordinates selected skill, confirmation dialog, run drawer, and opener restoration while preserving existing surfaces.

- [ ] Write failing tests for active recovery, terminal display-once, invalid/missing/expired clearing, no restart, no task/output/approval persistence, successful drawer transition, and existing map/activity/dashboard/search/drawers/status regressions.
- [ ] Run focused tests and verify failures.
- [ ] Implement minimal storage/recovery and page wiring.
- [ ] Re-run focused tests and existing component/page suites.
- [ ] Commit as `feat: add Hermes run recovery and dashboard integration`.

### Task 9: Documentation, security audit, and full verification

**Files:**
- Modify: `dashboard/README.md`
- Modify: `docs/superpowers/plans/2026-08-01-hermes-run-skill-plan.md` (mark completed checkboxes)

**Interfaces:** Documents setup, capability degradation, storage, security boundary, and safe manual test steps.

- [ ] Update README and run `rg` audits for `HERMES_API_KEY`, `NEXT_PUBLIC_HERMES`, `127.0.0.1:8642`, arbitrary proxy/path patterns, broad approval choices, and accidental task persistence.
- [ ] Run fresh `npm test` from `D:\Axion\dashboard`; record exact test-file/test counts and exit code.
- [ ] Run fresh `npm run lint`; record warnings/errors and exit code.
- [ ] Run fresh `npm run build`; record route list and exit code.
- [ ] If a safe local Hermes gateway is discoverable, start/inspect it and perform the harmless confirmation/SSE/recovery/stop/approval/network checks. Otherwise record the exact environmental blocker without claiming manual success.
- [ ] Review `git status --short`, `git diff --check`, and the global constraints; stage only README/plan or directly required fixes.
- [ ] Commit as `docs: document Phase B setup and testing`.

## Completion gate

Do not push. Do not claim completion unless all three automated commands exit successfully. The final report must list branch, commits, created/modified files, exact automated results, manual result, SSE/polling/approval/stop findings, secret isolation, trusted-installed enforcement, and Hermes-version limitations.
