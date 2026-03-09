---
description: "Start the Claude Viz live visualization server and open the browser panel. Call this before pushing any visualizations. The server runs on localhost:7891 and accepts POST requests with diagram content."
allowed-tools: Bash(bun *), Bash(curl *), Bash(open *), Bash(kill *), Bash(lsof *)
---

# Viz Start — Launch the Visualization Panel

## When to Use This Skill

- Before using `/visualize` for the first time in a session
- When the user asks to "open the viz panel" or "start visualization"
- Automatically called by the `/visualize` skill if the server is not running

## How to Start

### Step 1: Check if the server is already running

```bash
curl -s http://127.0.0.1:7891/api/health
```

If this returns `{"status":"ok",...}`, the server is already running. Skip to Step 3.

### Step 2: Start the server

```bash
bun run SKILL_BASE_DIR/../../server.ts &
```

Wait 1 second, then verify:

```bash
sleep 1 && curl -s http://127.0.0.1:7891/api/health
```

### Step 3: Open the browser

```bash
open http://127.0.0.1:7891
```

Tell the user: "Viz panel is open at http://127.0.0.1:7891 — place it next to your terminal."

### Step 4: Confirm

Tell the user the panel is ready. They should see a dark page with "Waiting for visualizations..." message.

## Stopping the Server

If the user asks to stop the viz server:

```bash
kill $(lsof -ti:7891) 2>/dev/null
```

## Troubleshooting

- **Port in use**: If port 7891 is taken, set a different port: `CLAUDE_VIZ_PORT=7892 bun run server.ts &`
- **Bun not installed**: Install with `curl -fsSL https://bun.sh/install | bash`
