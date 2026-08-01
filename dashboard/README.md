# AXION SkillTree Dashboard

The AXION SkillTree dashboard is a Next.js application with a secure server bridge to a locally running Hermes Agent API. Phase A resources remain read-only; Phase B can execute only AXION-trusted skills that Hermes currently reports as installed.

## Requirements

- Node.js 20 or newer
- npm 10 or newer
- A local Hermes Agent API listening on `http://127.0.0.1:8642` or another explicitly configured local URL

## Hermes environment

The Next.js server reads exactly these environment variables:

- `HERMES_API_URL` — optional; defaults to `http://127.0.0.1:8642`
- `HERMES_API_KEY` — optional only when the local Hermes API does not require bearer authentication

Place local values in `dashboard/.env.local`. That file and all local environment variants are ignored by Git. Never prefix these names with `NEXT_PUBLIC_`; browser code must not receive them.

```dotenv
HERMES_API_URL=http://127.0.0.1:8642
HERMES_API_KEY=replace-with-your-local-hermes-key
```

The example above is documentation only. Do not commit a real `.env.local`.

## Start locally

1. Start Hermes using the launch command provided by your Hermes installation, with its HTTP API bound to `127.0.0.1:8642`. Confirm it is available:

   ```bash
   curl http://127.0.0.1:8642/health
   ```

   If Hermes requires authentication, include the same bearer key configured as `HERMES_API_KEY`.

2. Start the dashboard:

   ```bash
   cd dashboard
   npm install
   npm run dev
   ```

3. Open [http://localhost:3000](http://localhost:3000).

## Security boundary

The browser calls only fixed `/api/hermes/*` AXION routes. Phase A reads still use the original GET-only client. Phase B uses a separate `server-only` client restricted to capabilities, installed skills, create/status/events/approval/stop operations. Every request uses `cache: "no-store"` and optional bearer authentication; there is no generic proxy, browser CORS requirement, arbitrary upstream path/method, raw upstream error body, API-key response, or session message-content response.

Gateway health refreshes every 15 seconds; overview and session summaries every 30 seconds; skills and toolsets every 60 seconds. Manual refresh cancels stale requests, overlapping requests are prevented, and temporary failures retain the last successful data.

AXION maps only the exact Hermes aliases `verified-ai-radar` and `verified-content-studio`. A run is enabled only when Hermes is online, run submission is advertised, and the matching alias is present in the latest `/v1/skills` response. The server repeats both trust and installation checks at submission time; the browser cannot select instructions, sessions, models, providers, tools, toolsets, commands, or paths.

## Phase B run behavior

- The user enters one 3–4000 character task and must choose **Confirm & Run**.
- SSE from `/api/hermes/runs/{id}/events` is primary. If the connected Hermes version lacks SSE but supports status, AXION displays **Live updates unavailable** and polls normalized status.
- Approval UI appears only when both approval response and approval events are advertised. AXION exposes only **Approve once** and **Deny**, translated to Hermes `{ "choice": "once" | "deny" }`.
- Stop requests remain **Stopping** until Hermes reports `cancelled`.
- Refresh recovery stores only run ID, trusted skill ID/name, and creation time. It never stores task text, output, approval payloads, tool data, or credentials and never restarts a task.

Current Hermes versions should advertise `run_submission`, `run_status`, `run_events_sse`, `run_stop`, `run_approval_response`, and `approval_events` under `/v1/capabilities`. AXION also recognizes `run_approval` as an older equivalent capability name.

For a safe manual check, start Hermes on its configured loopback URL, run `npm run dev`, choose an installed trusted skill, and submit a harmless read-only task. Verify browser network requests stay under `/api/hermes/`, refresh restores the drawer, and the browser bundle/payloads contain no `HERMES_API_KEY`. Use only a disposable harmless approval scenario; never test destructive commands.

## Quality commands

```bash
npm test
npm run lint
npm run build
```
