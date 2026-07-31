# AXION SkillTree Dashboard

The AXION SkillTree dashboard is a Next.js application with a Phase A read-only bridge to a locally running Hermes Agent API. It does not modify or execute the Python AXION application, and it does not execute Hermes skills.

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

The browser calls only fixed `/api/hermes/*` AXION routes. Those server routes call seven allowlisted Hermes GET endpoints with a five-second timeout and `cache: "no-store"`. There is no generic proxy, browser CORS support, arbitrary upstream path, write endpoint, raw upstream error body, API-key response, or session message-content response.

Gateway health refreshes every 15 seconds; overview and session summaries every 30 seconds; skills and toolsets every 60 seconds. Manual refresh cancels stale requests, overlapping requests are prevented, and temporary failures retain the last successful data.

Phase A maps only the exact Hermes aliases `verified-ai-radar` and `verified-content-studio`. Run execution is disabled and reserved for Phase B.

## Quality commands

```bash
npm test
npm run lint
npm run build
```
