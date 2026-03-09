---
description: "Push live visualizations (diagrams, architecture views, charts) to a browser side-panel while chatting. Supports Mermaid (client-side) and 20+ diagram types via Kroki (GraphViz, PlantUML, C4, D2, DBML, etc.). Use this whenever a visual would help the user understand what you're explaining."
context: fork
allowed-tools: Bash(curl *), Bash(bun *), Bash(open *), Bash(kill *), Bash(lsof *), Read, Grep, Glob
---

# Visualize — Push Dashboard Pages to the Side-Panel

## Your Task

Visualize: $ARGUMENTS

Analyze the relevant code, architecture, or concept described above. Choose the most appropriate diagram type(s), generate the diagram syntax, and push a dashboard page with one or more cards to the viz panel.

If no specific topic is given, explore the project structure and create an architectural overview.

## How It Works

1. A local Bun server runs at `http://127.0.0.1:7891`
2. You POST a **page** with multiple **cards** (diagrams, text, metrics) to `/api/pages`
3. The browser renders the page as a dashboard grid — cards can be full-width or half-width side-by-side
4. A sidebar shows page history — the user navigates between pages
5. Multiple Claude sessions share the same server, separated by session filters

## Step 0: Session Setup

On your first visualization, set up session identity. Do this ONCE, then reuse for all subsequent POSTs:

```bash
SESSION_ID=$(cat /dev/urandom | LC_ALL=C tr -dc 'a-z0-9' | head -c 6)
SESSION_NAME="$(basename $(pwd)) @ $(git branch --show-current 2>/dev/null || echo 'no-branch')"
```

## Step 1: Ensure the Server Is Running

```bash
curl -s http://127.0.0.1:7891/api/health 2>/dev/null || (bun run SKILL_BASE_DIR/../../server.ts & sleep 1 && open http://127.0.0.1:7891)
```

If the server wasn't running, tell the user: "Opening the viz panel — place the browser window next to your terminal."

## Step 2: Analyze and Generate

1. Read relevant source files using Read/Grep/Glob to understand the code or architecture
2. Choose the best diagram type(s) for each aspect
3. Plan a dashboard page: mix diagrams with text explanations and metrics
4. Push it as a single page with multiple cards

## Step 3: Push a Dashboard Page

Each POST creates a **page** containing one or more **cards** arranged in a 2-column grid.

Card `size`: `"full"` spans both columns (good for diagrams), `"half"` takes one column (good for text, metrics, small tables).

### Example: Mixed Dashboard Page

```bash
curl -s -X POST http://127.0.0.1:7891/api/pages \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Authentication System",
    "session_id": "'"$SESSION_ID"'",
    "session_name": "'"$SESSION_NAME"'",
    "source_files": ["/src/auth/login.ts", "/src/middleware/jwt.ts"],
    "cards": [
      {
        "type": "markdown",
        "title": "Overview",
        "size": "half",
        "content": "## Auth Flow\n\n- JWT-based authentication\n- Tokens expire after 24h\n- Refresh tokens stored in DB"
      },
      {
        "type": "html",
        "title": "Stats",
        "size": "half",
        "content": "<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:8px\"><div style=\"background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px;text-align:center\"><div style=\"font-size:24px;font-weight:700;color:#58a6ff\">3</div><div style=\"font-size:11px;color:#8b949e\">Services</div></div><div style=\"background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:12px;text-align:center\"><div style=\"font-size:24px;font-weight:700;color:#3fb950\">2</div><div style=\"font-size:11px;color:#8b949e\">Endpoints</div></div></div>"
      },
      {
        "type": "mermaid",
        "title": "Sequence Diagram",
        "size": "full",
        "content": "sequenceDiagram\n    participant C as Client\n    participant A as API\n    participant D as Database\n    C->>A: POST /login\n    A->>D: SELECT user\n    D-->>A: user record\n    A-->>C: JWT token"
      }
    ]
  }'
```

### Single-Card Page (simple)

For a quick single diagram, you can still use a single card:

```bash
curl -s -X POST http://127.0.0.1:7891/api/pages \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Data Flow",
    "session_id": "'"$SESSION_ID"'",
    "session_name": "'"$SESSION_NAME"'",
    "cards": [
      {
        "type": "mermaid",
        "size": "full",
        "content": "graph TD\n    A[Client] --> B[API] --> C[Database]"
      }
    ]
  }'
```

### Kroki Card (non-Mermaid diagram types)

```bash
{
  "type": "kroki",
  "title": "Dependency Graph",
  "size": "full",
  "content": "digraph G { rankdir=LR; Client -> API -> DB }",
  "kroki_diagram_type": "graphviz"
}
```

## API Reference

### POST /api/pages

| Field | Type | Required | Description |
|---|---|---|---|
| `title` | string | yes | Page title shown in sidebar and header |
| `cards` | array | yes | Array of card objects (see below) |
| `session_id` | string | no | Session identifier (reuse across all POSTs) |
| `session_name` | string | no | Display name for session filter |
| `source_files` | string[] | no | File paths — shown as clickable links on the page |

### Card Object

| Field | Type | Required | Description |
|---|---|---|---|
| `type` | string | yes | `"mermaid"`, `"kroki"`, `"html"`, `"svg"`, `"markdown"` |
| `title` | string | no | Card header label |
| `content` | string | yes | Diagram source, HTML, SVG, or markdown |
| `size` | string | no | `"full"` (default, spans 2 columns) or `"half"` (1 column) |
| `kroki_diagram_type` | string | if type=kroki | `"graphviz"`, `"plantuml"`, `"c4plantuml"`, `"d2"`, `"dbml"`, etc. |
| `kroki_output_format` | string | no | `"svg"` (default) or `"png"` |

## Dashboard Layout Tips

- **Mix card types.** A good page combines a diagram with text explanation and maybe metrics.
- **Use half-width** for text, small tables, and stats grids.
- **Use full-width** for diagrams, large tables, and code blocks.
- **Two half cards** next to each other create a nice side-by-side layout.
- **Keep pages focused.** One topic per page. Push multiple pages for different topics.

## Which Diagram Type to Use

**Default to Mermaid** unless you need something specific:

| Need | Use | Type |
|---|---|---|
| Flowchart, decision tree | Mermaid `graph TD` / `flowchart` | `mermaid` |
| Sequence diagram | Mermaid `sequenceDiagram` | `mermaid` |
| ER diagram (quick) | Mermaid `erDiagram` | `mermaid` |
| Class diagram | Mermaid `classDiagram` | `mermaid` |
| State machine | Mermaid `stateDiagram-v2` | `mermaid` |
| Gantt chart | Mermaid `gantt` | `mermaid` |
| C4 architecture diagram | C4 PlantUML | `kroki` + `c4plantuml` |
| Infrastructure / deployment | D2 | `kroki` + `d2` |
| Database schema (detailed) | DBML | `kroki` + `dbml` |
| Dependency / call graph | GraphViz DOT | `kroki` + `graphviz` |
| Mind map | PlantUML `@startmindmap` | `kroki` + `plantuml` |
| Data chart (bar, line, etc.) | Vega-Lite | `kroki` + `vegalite` |

For detailed syntax examples of each Kroki diagram type, read `SKILL_BASE_DIR/kroki-reference.md`.

## After Pushing

Report back what you visualized:
- Page title and number of cards
- What the dashboard shows (one sentence)
- Source files analyzed

This summary is returned to the main conversation.
