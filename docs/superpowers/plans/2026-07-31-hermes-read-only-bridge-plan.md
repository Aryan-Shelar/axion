# AXION Hermes Read-Only Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a secure read-only Hermes data bridge and reflect normalized live state in the existing SkillTree dashboard.

**Architecture:** Browser components consume fixed AXION API routes and never contact Hermes. Server-only modules enforce a strict upstream path union, authentication, timeout, no-store fetches, normalization, and safe error envelopes; client hooks poll each independent resource without overlap and preserve stale success data.

**Tech Stack:** Next.js 15 App Router, React 19, TypeScript, Vitest, Testing Library, native Fetch and AbortController.

## Global Constraints

- Do not modify the existing Python AXION application.
- Phase A is read-only; do not implement Run Skill execution.
- Never expose or log `HERMES_API_KEY` and never enable browser CORS.
- Permit only the seven approved fixed upstream GET paths; no generic proxy or arbitrary URL/path input.
- Do not return complete session message content.
- Preserve all existing dashboard interactions.
- Use TDD and small commits in the requested task order.

---

### Task 1: Types, errors, normalization, aliases, and environment ignores

**Files:** Create `dashboard/src/lib/hermes/types.ts`, `errors.ts`, `normalize.ts`, `skill-aliases.ts` and colocated tests; modify `dashboard/.gitignore`.

**Interfaces:** Produce `HermesPath`, `HermesPublicError`, normalized resource types, `normalizeHealth`, `normalizeOverviewParts`, `normalizeSkills`, `normalizeToolsets`, `normalizeSessions`, `toPublicHermesError`, and `getAxionSkillInstallation`.

- [ ] Write failing tests using literal upstream fixtures for malformed shapes, offline/auth mapping, exact aliases, and removal of `messages`, `content`, tokens, keys, paths, and nested sensitive values.
- [ ] Run `npm test -- src/lib/hermes` and confirm failures are caused by missing modules/behavior.
- [ ] Implement minimal types, guards, normalization, safe error mapping, exact alias matching, and `.env` ignore entries.
- [ ] Run the focused tests and the existing suite.
- [ ] Commit with `git commit -m "feat(dashboard): add Hermes normalization contracts"`.

### Task 2: Server-only Hermes client

**Files:** Create `dashboard/src/lib/hermes/client.ts` and `client.test.ts`.

**Interfaces:** Produce `hermesGet(path: HermesPath, options?: { signal?: AbortSignal; fetchImpl?: typeof fetch })` using server-only environment configuration, five-second abort, `cache: "no-store"`, and optional bearer auth.

- [ ] Write failing tests proving default/base URL behavior, bearer header handling without exposure, timeout abort, no-store fetches, external abort propagation, and safe handling of 401/403 and bad JSON.
- [ ] Run the client test and confirm RED.
- [ ] Implement the fixed-path GET client without a generic string path or URL argument.
- [ ] Run focused and full tests.
- [ ] Commit with `git commit -m "feat(dashboard): add server-only Hermes client"`.

### Task 3: AXION read-only API routes

**Files:** Create route handlers under `dashboard/src/app/api/hermes/{health,overview,skills,toolsets,sessions}/route.ts`, a small server response helper if needed, and route tests.

**Interfaces:** Each `GET()` returns a normalized `{ data, error, refreshedAt }` response; overview uses independently settled requests so one upstream failure cannot break unrelated fields.

- [ ] Write route tests with controlled client responses for success, partial overview, offline, authentication, and malformed data.
- [ ] Run route tests and confirm RED.
- [ ] Implement fixed GET handlers and stable status codes without upstream bodies or secrets.
- [ ] Run focused and full tests.
- [ ] Commit with `git commit -m "feat(dashboard): expose read-only Hermes routes"`.

### Task 4: Polling hooks

**Files:** Create `dashboard/src/hooks/use-hermes-resource.ts`, `use-hermes-dashboard.ts`, and tests.

**Interfaces:** Produce a reusable resource state `{ data, error, loading, refreshing, lastSuccessAt, refresh }` and a composed dashboard hook with 15/30/60-second schedules.

- [ ] Write fake-timer tests for immediate load, interval scheduling, cleanup abort, stale-request cancellation, overlap prevention, manual refresh, and last-success retention.
- [ ] Run hook tests and confirm RED.
- [ ] Implement abort-aware resource polling and the composed Hermes hook.
- [ ] Run focused and full tests.
- [ ] Commit with `git commit -m "feat(dashboard): poll Hermes read-only resources"`.

### Task 5: Gateway and overview UI

**Files:** Modify `top-navigation.tsx`, `dashboard-overview.tsx`, `page.tsx`, styles, and component tests.

**Interfaces:** Top navigation consumes normalized gateway state; overview consumes independent resource states and manual `refreshAll`.

- [ ] Write failing tests for all five gateway labels, readiness/model/profile/counts/active work/last refresh, manual refresh, and loading/offline/partial unavailable states.
- [ ] Run focused tests and confirm RED.
- [ ] Wire the composed hook at page scope and render the live gateway and overview panels without removing existing navigation.
- [ ] Run focused and full tests.
- [ ] Commit with `git commit -m "feat(dashboard): show live Hermes overview"`.

### Task 6: SkillTree installation integration

**Files:** Modify `skill-tree-canvas.tsx`, `nodes/skill-node.tsx`, `skill-detail-drawer.tsx`, `page.tsx`, styles, and tests.

**Interfaces:** Components consume the installed alias set plus availability state and render one of the three exact installation labels.

- [ ] Write failing tests for installed aliases, unmatched prototypes, unavailable status, preserved selection/search behavior, and a disabled `Available in Phase B` button.
- [ ] Run focused tests and confirm RED.
- [ ] Add installation state to nodes/drawer and disable Phase B execution while retaining Edit/History feedback.
- [ ] Run focused and full tests.
- [ ] Commit with `git commit -m "feat(dashboard): map Hermes skill installations"`.

### Task 7: Documentation and final verification

**Files:** Modify `dashboard/README.md`; verify both documents under `docs/superpowers`.

**Interfaces:** Document only `HERMES_API_URL` and `HERMES_API_KEY`, local startup, security boundary, polling, and Phase A limitations.

- [ ] Update the README without creating a real `.env.local`.
- [ ] Run `rg` checks for browser Hermes URLs, secret exposure, generic proxy patterns, and Python-file changes.
- [ ] Run `npm test`, `npm run lint`, and `npm run build`; fix every failure and rerun all three.
- [ ] Review the final diff against every requirement in the approved design.
- [ ] Commit with `git commit -m "docs(dashboard): document Hermes bridge setup"`.
