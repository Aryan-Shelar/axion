# AXION Hermes Read-Only Bridge Design

## Status

Approved by the repository owner on 2026-07-31. This document records Phase A only; Hermes execution remains Phase B.

## Goal

Connect the Next.js SkillTree dashboard to a locally running Hermes Agent API through a secure, read-only server boundary while preserving the existing map, activity, dashboard, search, drawer, navigation, zoom, fit-view, and minimap behavior.

## Architecture and trust boundary

The only data path is `Browser -> AXION Next.js API routes -> Hermes API at http://127.0.0.1:8642`. Browser code calls only `/api/hermes/*`. Server-only code reads `HERMES_API_URL` and `HERMES_API_KEY`, adds bearer authentication, enforces a five-second timeout and `cache: "no-store"`, and accepts only a TypeScript union of seven fixed GET paths. There is no browser CORS configuration, arbitrary path input, generic proxy, API-key logging, or API-key response field.

Allowed upstream paths are `/health`, `/health/detailed`, `/v1/capabilities`, `/v1/models`, `/v1/skills`, `/v1/toolsets`, and `/api/sessions`. AXION exposes only `/api/hermes/health`, `/api/hermes/overview`, `/api/hermes/skills`, `/api/hermes/toolsets`, and `/api/hermes/sessions`.

## Modules and contracts

- `types.ts` owns upstream-safe unknown records, normalized gateway status, overview, skill, toolset, and session summaries, route envelopes, and the strict upstream path union.
- `errors.ts` maps abort/timeout, connection failures, 401/403, non-success HTTP status, and malformed data to stable public error codes and messages.
- `client.ts` is server-only and performs fixed-path GET requests. It never accepts a full URL and never returns upstream error bodies.
- `normalize.ts` validates unknown JSON and emits minimal dashboard contracts. Session normalization removes message content and sensitive fields.
- `skill-aliases.ts` contains the exact Phase A aliases `verified-ai-radar` and `verified-content-studio`; no fuzzy matching is allowed.

## Route composition

Each route catches errors independently and returns a normalized JSON envelope. Health reads `/health` and may enrich from `/health/detailed`. Overview independently requests capabilities, models, health detail, skills, toolsets, and sessions and preserves partial successes. Dedicated skills, toolsets, and sessions routes expose only normalized summaries. A malformed or failed endpoint marks only its panel unavailable.

## Client state and polling

A focused polling hook owns each resource interval: health 15 seconds, overview and sessions 30 seconds, skills and toolsets 60 seconds. A shared poller prevents overlap, aborts stale requests on refresh/unmount, retains the last successful payload during temporary failures, and provides manual refresh. Gateway status maps loading, ready, degraded, offline, and authentication failures to the required labels.

## UI behavior

The top navigation reports `Checking Hermes`, `Hermes Online`, `Hermes Degraded`, `Hermes Offline`, or `Authentication Error`. Dashboard overview panels show readiness, advertised model/profile, installed skill count, toolset count, recent session count, active runs/delegations when present, and last successful refresh, with independent loading/unavailable states.

Installed Hermes aliases mark the corresponding AXION nodes and drawer as `Installed in Hermes`; unmatched nodes are `Prototype skill`; when Hermes data is unavailable the label is `Installation status unavailable`. The Run button is disabled and reads `Available in Phase B`. Edit and History retain visible prototype feedback.

## Failure and privacy behavior

Connection refusal and timeout map to offline; HTTP 401/403 maps to authentication error; non-ready health maps to degraded. Malformed JSON or shapes map to panel-level unavailable. UI responses contain no raw upstream body, stack trace, local path, session message content, credential, token, or API key.

## Verification

Tests cover normalization, sensitive-field removal, error mapping, timeout, exact aliases, route success/failure, polling cleanup/abort/non-overlap/retention, gateway labels, dashboard loading/offline states, installation labels, and the disabled Phase B control. Completion requires `npm test`, `npm run lint`, and `npm run build` to exit successfully.
