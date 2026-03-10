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
        "type": "kroki",
        "title": "Sequence Diagram",
        "size": "full",
        "content": "@startuml\nactor User\nparticipant \"Web App\" as WA\nparticipant \"Auth Service\" as Auth\ndatabase \"User DB\" as DB\nUser -> WA: Login(email, pass)\nWA -> Auth: Authenticate\nAuth -> DB: SELECT user\nDB --> Auth: record\nAuth --> WA: JWT\nWA --> User: Set-Cookie\n@enduml",
        "kroki_diagram_type": "plantuml"
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
- **Two half cards** next to each other create a nice side-by-side layout.
- **Keep pages focused.** One topic per page. Push multiple pages for different topics.

### Choosing `full` vs `half` for diagram cards

Diagram cards have zoom/pan built in (scroll to zoom, drag to pan), so even large diagrams fit in a card. Choose the size based on the **natural shape** of the diagram:

**Use `"full"` (spans both columns) when the diagram is wide/landscape:**
- Flowcharts with `direction: LR` or `right` (horizontal flow)
- Sequence diagrams with **4+ participants** (many columns)
- ER/DBML diagrams with **4+ tables** arranged horizontally
- Component/deployment diagrams with many side-by-side boxes
- GraphViz with `rankdir=LR`
- Wide C4 container diagrams

**Use `"half"` (one column) when the diagram is tall/narrow or small:**
- Sequence diagrams with **2–3 participants** (few columns, tall)
- State diagrams, mind maps
- Small class diagrams (1–3 classes)
- DBML/ER with **2–3 tables**
- Pie charts, small bar charts
- Simple flowcharts with `direction: TB` (vertical)

**Rule of thumb:** If the diagram has more horizontal extent than vertical, use `full`. If it's taller than wide or would look fine in half the space, use `half`. When in doubt, use `half` — the user can always expand to fullscreen.

### Non-diagram cards

- **Use `"half"`** for markdown text, tables, stats grids, and small HTML cards.
- **Use `"full"`** only for wide tables (4+ columns) or large HTML dashboards.

## Which Diagram Type to Use

**Prefer Kroki** for richer, better-looking diagrams. Use Mermaid only for quick simple cases.

**Vary your diagram types** — do not always pick the same one. Match the diagram tool to the content.

| Need | Best Choice | Type | Alternative |
|---|---|---|---|
| Architecture (C4 model) | C4 PlantUML | `kroki` + `c4plantuml` | `kroki` + `structurizr` |
| Architecture (informal) | D2 | `kroki` + `d2` | `kroki` + `graphviz` |
| Database schema / ER | DBML | `kroki` + `dbml` | Mermaid `erDiagram` |
| Sequence diagram | PlantUML | `kroki` + `plantuml` | Mermaid `sequenceDiagram` |
| Flowchart | D2 or GraphViz | `kroki` + `d2` / `graphviz` | Mermaid `flowchart` |
| Class diagram | PlantUML | `kroki` + `plantuml` | Mermaid `classDiagram` |
| Dependency / call graph | GraphViz DOT | `kroki` + `graphviz` | — |
| Network topology | NwDiag or GraphViz | `kroki` + `nwdiag` / `graphviz` | — |
| Mind map | PlantUML | `kroki` + `plantuml` | Mermaid `mindmap` |
| State machine | PlantUML | `kroki` + `plantuml` | Mermaid `stateDiagram-v2` |
| Data chart (bar, line, etc.) | Vega-Lite | `kroki` + `vegalite` | — |
| Gantt chart | Mermaid `gantt` | `mermaid` | — |
| ASCII art to diagram | SvgBob | `kroki` + `svgbob` | — |
| Server rack layout | RackDiag | `kroki` + `rackdiag` | — |

**When to use Mermaid:** Only for very simple diagrams where the quick client-side rendering is worth the simpler output. For anything complex or polished, use Kroki.

For detailed syntax examples of each Kroki diagram type, read `SKILL_BASE_DIR/kroki-reference.md`.

## Important: Colors and Theming

**Kroki diagrams (PlantUML, GraphViz, DBML, etc.) render on a LIGHT background by default.** The viz panel auto-sets a light background for Kroki and SVG cards. Therefore:

- **Do NOT add dark theme `skinparam` overrides** to PlantUML diagrams (e.g., `skinparam backgroundColor #0d1117`). This will make the diagram unreadable — dark lines on a dark background.
- **Use default PlantUML colors** — they are designed for light backgrounds and look great out of the box.
- **For GraphViz**, use light fill colors like `fillcolor=lightyellow`, `fillcolor=lightblue`, `fillcolor=lightgreen` for nodes.
- **For D2**, default colors work well on light backgrounds.
- The user can toggle dark/light background per card using the toggle button in the card header.

**Mermaid diagrams render on a DARK background** (the viz panel's native dark theme). Mermaid uses its built-in `dark` theme, but **custom `style` directives override the theme's text color**. When you set a custom `fill` on a node, the text color reverts to Mermaid's default (light gray) which becomes unreadable on light fills.

**CRITICAL — Always set explicit text `color` in Mermaid `style` directives:**

- **Light fill** (e.g., `#c8e6c9`, `#e3f2fd`, `#fff8e1`, `#fff9c4`, `#ffccbc`, `#fce4ec`, `#f3e5f5`, `#ffcdd2`, `#ffebee`) → use `color:#000`
- **Dark fill** (e.g., `#333`, `#444`, `#1565C0`, `#2E7D32`, `#C62828`, `#7B1FA2`) → use `color:#fff`
- **Example:** `style NODE fill:#c8e6c9,stroke:#2E7D32,color:#000`
- **Every `style` line must include `color`** — never omit it when setting a custom `fill`.

## Important: Markdown Tables

Markdown cards support pipe-delimited tables:

```markdown
| Column 1 | Column 2 | Column 3 |
|---|---|---|
| Cell A | Cell B | Cell C |
| **Bold** | `code` | *italic* |
```

Tables must have:
- A header row (first row)
- A separator row with dashes (`|---|---|---|`)
- One or more data rows

**Do NOT embed tables in the middle of other markdown content** — the table must be the entire content of the block (separated by blank lines from surrounding text). If you need both text and a table, use separate cards (one `markdown` card for text, another `markdown` card for the table) or use an `html` card for full control.

## Diagram Interactivity

All diagram cards (mermaid, kroki, svg) have built-in zoom and pan:

- **Scroll wheel** to zoom in/out (anchored to cursor position)
- **Click and drag** to pan around the diagram
- Diagrams **auto-scale to fit** inside a 500px-tall card on load
- **Fullscreen button** (in card header) opens a full-viewport overlay with:
  - `+` / `−` / `1:1` zoom toolbar buttons
  - Scroll-wheel zoom and drag-to-pan
  - `Esc` to close

Because diagrams auto-scale, the `size` choice (`full` vs `half`) is about **layout efficiency**, not about fitting content. A tall sequence diagram in a `full`-width card wastes horizontal space — put it in `half` so another card can sit beside it.

## After Pushing

Report back what you visualized:
- Page title and number of cards
- What the dashboard shows (one sentence)
- Source files analyzed

This summary is returned to the main conversation.
