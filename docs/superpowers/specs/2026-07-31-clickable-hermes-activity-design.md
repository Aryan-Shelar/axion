# Clickable Hermes Activity Design

## Status

Approved by the repository owner on 2026-07-31. This design extends the existing Phase A read-only Hermes bridge; it does not add Phase B execution.

## Goal and boundaries

Replace normal use of the static Activity fixture with the existing normalized Hermes session resource. Both the full Activity view and compact Map panel consume `useHermesDashboard().sessions`; no component creates another request or polling loop. Only safe session scalars reach the browser: `id`, `title`, optional `source`, optional `status`, and optional `updatedAt`.

No message history, prompt, tool argument, output, secret, raw upstream object, write control, or execution control is rendered or returned.

## Data normalization

`HermesSessionSummary` gains optional `source`. `normalizeSessions` constructs a new summary object field by field and never spreads an upstream session. String guards accept only non-empty scalar strings. Existing message-content and sensitive-field removal tests remain authoritative.

## Ordering and presentation

`session-activity.ts` exports a stable newest-first sorter and display helpers. Valid timestamps sort descending. Invalid or missing timestamps follow all dated sessions. Equal timestamps and undated sessions preserve their input order through an explicit original-index tie breaker.

`ActivityPanel` accepts the sessions resource state, selection callback, refresh callback, expanded/compact mode, and optional open-full-Activity callback. Rows are native `<button>` elements, so click, Enter, and Space activation use built-in semantics. Full mode renders all sorted sessions and a manual Refresh button; compact mode renders the newest three and an arrow that changes the application view to Activity.

Loading renders a clear first-load state. An empty successful list renders exactly `No Hermes activity yet.` A temporary offline/authentication error with retained data renders a non-blocking warning above that data. An error without retained data renders only a safe unavailable/authentication state. Demo events are never used as a fallback.

## Drawer accessibility

`SessionDetailDrawer` matches the existing right-side drawer treatment and renders only title, session ID, source, status, and last updated. It uses `role="dialog"`, `aria-modal="true"`, an accessible name, close button, and backdrop close.

On open it records the opener supplied by the session row, focuses the close button, traps Tab and Shift+Tab within the drawer, and closes on Escape. On close/unmount it restores focus to the opener when still connected. There are no footer actions or write controls.

## State ownership

`page.tsx` continues to call `useHermesDashboard()` once. It passes `hermes.sessions.data`, `loading`, `error`, and `refresh` into both Activity surfaces and holds the selected session plus opener element. Changing tabs does not start or stop a second polling source. SkillTree, gateway, search, Map controls, Dashboard overview, and status behavior are unchanged.

## Verification

Focused tests cover safe normalization, stable sorting, real-session rows, all resource states, native keyboard activation, drawer metadata and modal behavior, focus trap/restoration, compact three-row behavior, Activity navigation, absence of sensitive content, and absence of write controls. Completion requires clean `npm test`, `npm run lint`, and `npm run build` runs.
