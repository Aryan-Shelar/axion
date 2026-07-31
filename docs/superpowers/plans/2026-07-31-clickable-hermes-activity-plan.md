# Clickable Hermes Activity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Render real, clickable Hermes sessions in both Activity surfaces with a safe accessible metadata drawer.

**Architecture:** The existing page-level Hermes hook remains the sole polling owner. A pure session helper normalizes ordering/display, a controlled Activity panel renders resource states and native buttons, and a focused modal drawer owns keyboard/focus behavior.

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript, Vitest, Testing Library, Framer Motion.

## Global Constraints

- Preserve the existing Hermes connection, Map, Dashboard, SkillTree, search, and status behavior.
- Reuse `useHermesDashboard().sessions`, its 30-second polling, and its refresh method; create no second poller.
- Render only safe session metadata; never expose messages, prompts, tool arguments, outputs, secrets, or raw upstream objects.
- Add no write controls or Phase B execution.
- Follow test-driven development and small commits.

---

### Task 1: Session type and normalization

**Files:** Modify `dashboard/src/lib/hermes/types.ts`, `normalize.ts`, and `normalize.test.ts`.

**Interfaces:** `HermesSessionSummary` adds `source?: string`; `normalizeSessions(value)` returns newly constructed safe scalar summaries.

- [x] Add failing literal-fixture tests for source and for removal of messages, prompts, tool arguments, outputs, secrets, and nested data.
- [x] Run `npm test -- src/lib/hermes/normalize.test.ts` and confirm RED.
- [x] Implement field-by-field source normalization without spreading upstream objects.
- [x] Run focused tests; commit `feat(dashboard): normalize Hermes activity sessions`.

### Task 2: Sorting and display helpers

**Files:** Create `dashboard/src/lib/hermes/session-activity.ts` and `.test.ts`.

**Interfaces:** Export `sortSessionsNewestFirst(sessions)`, `sessionSecondaryText(session)`, and `formatSessionUpdatedAt(value)`.

- [x] Add failing tests for descending valid timestamps and stable equal/missing/invalid timestamp ordering.
- [x] Run the helper test and confirm RED.
- [x] Implement a copy-on-sort with original-index tie breaking and safe display fallbacks.
- [x] Run focused tests; commit `feat(dashboard): order Hermes session activity`.

### Task 3: Real Activity list and states

**Files:** Rewrite `dashboard/src/components/activity-panel.tsx`; create/update component tests and CSS.

**Interfaces:** Panel props provide sessions, loading, error, refresh, selection, mode, and optional full-view navigation.

- [x] Add failing tests for real sessions, loading, exact empty copy, offline/auth warnings, retained data, refresh, click, Enter, Space, and absence of demo/sensitive/write content.
- [x] Run focused tests and confirm RED.
- [x] Implement native button rows and independent safe states using the pure helper.
- [x] Run focused tests; commit `feat(dashboard): render real Hermes activity`.

### Task 4: Session detail drawer

**Files:** Create `dashboard/src/components/session-detail-drawer.tsx` and `.test.tsx`; modify CSS.

**Interfaces:** Drawer props are `session`, `opener`, and `onClose`; drawer renders only the five approved fields.

- [x] Add failing tests for metadata, close/backdrop/Escape, focus trap, focus restoration, accessible dialog semantics, and absence of forbidden controls/content.
- [x] Run focused tests and confirm RED.
- [x] Implement modal keyboard/focus lifecycle and safe metadata rendering.
- [x] Run focused tests; commit `feat(dashboard): add session metadata drawer`.

### Task 5: Page integration and compact Map navigation

**Files:** Modify `dashboard/src/app/page.tsx` and integration/component tests.

**Interfaces:** The single existing Hermes hook feeds both panels; page owns selected session/opener and the compact arrow calls `setView("activity")`.

- [x] Add failing tests for three-row compact output, full-list output, arrow navigation, selection/drawer wiring, and shared refresh usage.
- [x] Run focused tests and confirm RED.
- [x] Remove normal `activityEvents` imports and wire the existing sessions resource to both panels and the drawer.
- [x] Run focused tests; commit `feat(dashboard): connect Hermes activity surfaces`.

### Task 6: Documentation and final verification

**Files:** Verify the requested design/plan and update `dashboard/README.md` only if user-facing behavior needs clarification.

**Interfaces:** Documentation states that Activity is real read-only session metadata and Phase B remains unavailable.

- [x] Scan normal runtime code for `activityEvents`, session spreads, message/prompt/output rendering, and write controls.
- [x] Run `npm test`, `npm run lint`, and `npm run build`; fix and rerun every failure.
- [x] Review the final diff for Python changes and unrelated files.
- [x] Commit the feature documentation and final verification record.
