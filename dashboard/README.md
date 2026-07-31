# AXION SkillTree Dashboard

Version 1 of the standalone AXION visual operating dashboard. It is a frontend-only Next.js application with local mock data; it does not connect to the Python assistant or any external API.

## Requirements

- Node.js 20 or newer
- npm 10 or newer

## Run locally

```bash
cd dashboard
npm install
npm run dev
```

Open [http://localhost:3000](http://localhost:3000). Click specialist nodes for details, drag the canvas to pan, scroll to zoom, or use the lower-right map controls.

## Quality commands

```bash
npm test
npm run lint
npm run build
npm start
```

## Structure

- `src/app` — App Router shell, route, loading UI, and global visual system
- `src/components` — navigation, graph nodes, canvas, activity, overview, and detail drawer
- `src/data` — typed department, skill, topology, and activity fixtures
- `src/types` — shared domain types
- `src/lib` — presentation helpers

All data is local and intentionally ready to replace with authenticated services in a future phase.
