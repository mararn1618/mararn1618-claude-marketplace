---
name: markdown-to-everywhere
description: "Markdown to Everywhere: write architecture docs in markdown with status badges, multi-column layouts (2 or 3 columns), and draw.io diagram references, then publish to HTML or Confluence Cloud. Use this skill whenever the user wants to write architecture docs, render markdown to HTML, publish docs to Confluence, convert markdown to Confluence storage format, generate draw.io diagrams programmatically from Python, embed diagrams in HTML or Confluence, create status badges, set up a documentation pipeline, or mentions render_html.py, publish_confluence.py, drawio_helpers.py, or the doc pipeline. Also use when the user needs to understand draw.io XML format, mxGraphModel structure, CLI export, edge routing, containers, or style properties."
---

# Doc Pipeline

Four-stage architecture documentation pipeline: **Markdown** (author) -> **Draw.io** (diagrams) -> **HTML** (render) -> **Confluence** (publish). Each stage runs independently. Zero external Python dependencies.

## Bundled Scripts

Three reusable Python scripts ship with this skill. Copy them into your project and adapt.

| Script | Purpose |
|--------|---------|
| `${CLAUDE_PLUGIN_ROOT}/skills/markdown-to-everywhere/scripts/render_html.py` | Markdown to self-contained HTML with interactive draw.io diagrams, status badges, two-column layouts |
| `${CLAUDE_PLUGIN_ROOT}/skills/markdown-to-everywhere/scripts/publish_confluence.py` | Markdown to Confluence Cloud via REST API (badges, draw.io embeds, layouts, code blocks) |
| `${CLAUDE_PLUGIN_ROOT}/skills/markdown-to-everywhere/scripts/drawio_helpers.py` | Shared draw.io generation helpers: STYLES dict, ERD builder, legend, ID-prefixing writer |

## Quick Start

```bash
# 1. Copy scripts into your project
cp ${CLAUDE_PLUGIN_ROOT}/skills/markdown-to-everywhere/scripts/drawio_helpers.py diagrams/
cp ${CLAUDE_PLUGIN_ROOT}/skills/markdown-to-everywhere/scripts/render_html.py html/

# 2. Write your diagram generator (imports drawio_helpers)
python3 diagrams/generate.py

# 3. Render HTML
python3 html/render_html.py .

# 4. Serve (HTTP required for draw.io viewer)
cd html && python3 -m http.server 8765

# 5. Publish to Confluence (optional)
python3 publish_confluence.py --config confluence.json
```

---

## Stage 1: Markdown Authoring

### Status Badges

Tag every section header to show what is existing vs proposed:

```markdown
## Config Data Model [EXISTING]
## Pipeline Split [NEW]
## Scheduling [CHANGED]
## Inbound Processing [NEW: GREENFIELD]
```

Tokens: `[NEW]`, `[EXISTING]`, `[CHANGED]`, `[GREENFIELD]`, `[REVISED]`, and compounds `[NEW: GREENFIELD]`, `[EXISTING/CHANGED]`.

### Two-Column Layouts

```markdown
<!-- columns -->
![Config ERD](diagrams/10-config-erd.drawio)

<!-- col -->
**Key points:**
- Bullet 1
- Bullet 2
<!-- /columns -->
```

Use for **tall/square diagrams + 3-8 bullets**. Not for wide pipeline diagrams.

### Diagram References

```markdown
![Outbound Pipeline](diagrams/03-outbound-pipeline.drawio)
```

### Key Rules

- Files named `NN-topic.md` (auto-discovered by renderer)
- Every `[NEW]` section gets a "Concept: Why..." explanation
- No em dashes or `--` as dashes
- No people names in docs (use role/team references)

Full conventions: [references/markdown-conventions.md](references/markdown-conventions.md)

---

## Stage 2: Draw.io Diagrams

### Programmatic Generation (Python)

Generate diagrams from Python using `drawio_helpers.py`:

```python
from drawio_helpers import STYLES, make_erd_entity, make_legend, write_diagram
from pathlib import Path

def gen_my_diagram():
    cells = []
    cells.append({"id": "extract", "value": "<b>Extract</b>",
                   "style": STYLES["process"], "x": 100, "y": 100, "w": 160, "h": 60})
    cells.append({"id": "store", "value": "<b>Outbox</b>",
                   "style": STYLES["store_existing"], "x": 350, "y": 100, "w": 120, "h": 60})
    cells.append({"id": "e1", "source": "extract", "target": "store",
                   "style": STYLES["arrow"], "label": "writes"})
    cells.extend(make_legend(500, 250))
    return cells

write_diagram(Path("diagrams/01-my-diagram.drawio"), "My Diagram", gen_my_diagram())
```

### Seven Entity Categories (mandatory color scheme)

| Category | Fill | Stroke | Style key |
|----------|------|--------|-----------|
| Processing stage | salmon `#FFB3BA` | `#CC4455` | `process` |
| Store (existing) | green `#BAFFC9` | `#339944` | `store_existing` (cylinder) |
| Store (new) | lemon `#FFFACD` | `#CC9900` | `store_new` (cylinder) |
| Core system | steel blue `#D4E6F1` | `#1A5276` | `core_system` (bold, thick border) |
| External party | light blue `#BAE1FF` | `#2266AA` | `external` |
| Cloud service | pale yellow `#FFFFBA` | `#CC8800` | `btp` (dashed border) |
| New component | lavender `#E8DAEF` | `#7744AA` | `new_component` |

### ERD Entities

```python
cells, height = make_erd_entity("parties", "de_parties", "EXISTING",
    ["party_id", "name", "type"], "erd_existing", x=100, y=100, w=180)
```

Edges connect to `{entity_id}_fields`, not the parent container.

### Critical Rules

1. **Always use `write_diagram()`** to prefix cell IDs (prevents `d.setId` crashes)
2. **Always include `html=1;`** in styles using HTML tags
3. **Never use `ERmany`/`ERone`** markers; use `classic`/`oval` arrows
4. **Every diagram gets a legend** via `make_legend(x, y)`
5. **Every edge must have `<mxGeometry relative="1" as="geometry"/>`**

### Direct XML (without helpers)

For one-off diagrams, write draw.io XML directly:

```xml
<mxGraphModel>
  <root>
    <mxCell id="0"/>
    <mxCell id="1" parent="0"/>
    <mxCell id="2" value="Box" style="rounded=1;whiteSpace=wrap;" vertex="1" parent="1">
      <mxGeometry x="100" y="100" width="120" height="60" as="geometry"/>
    </mxCell>
  </root>
</mxGraphModel>
```

### CLI Export

```bash
# macOS
/Applications/draw.io.app/Contents/MacOS/draw.io -x -f png -e -b 10 -o out.drawio.png in.drawio

# Linux
drawio -x -f svg -e -o out.drawio.svg in.drawio
```

PNG/SVG/PDF with `--embed-diagram` remain editable in draw.io. Use double extensions: `name.drawio.png`.

Full draw.io XML reference: [references/drawio-format.md](references/drawio-format.md)

---

## Stage 3: HTML Rendering

The `render_html.py` script converts markdown to self-contained HTML.

### How it works

1. Auto-discovers `NN-*.md` files in the base directory
2. Converts each to HTML with embedded CSS (no external stylesheets)
3. Copies `.drawio` files to `html/` for the interactive viewer
4. Generates navigation bar and index page
5. Draw.io diagrams are interactive (zoom, layers, lightbox)

### Usage

```bash
python3 render_html.py /path/to/docs
cd /path/to/docs/html && python3 -m http.server 8765
```

### Draw.io embedding approach

Diagrams are loaded by URL via the viewer-static.min.js CDN script:
```html
<div class="mxgraph" data-mxgraph='{"url":"filename.drawio"}'></div>
```

**Never inline draw.io XML in HTML attributes** (encoding chains break). **Always serve via HTTP** (file:// does not work).

Full renderer details: [references/html-rendering.md](references/html-rendering.md) (if created)

---

## Stage 4: Confluence Publishing

The `publish_confluence.py` script publishes markdown to Confluence Cloud.

### Three-step process

1. **Upload `.drawio` attachments** to each page
2. **Convert markdown** to Confluence storage format (status macros, drawio macros, layouts)
3. **PUT page** with incremented version number

### Config file

```json
{
  "base_url": "https://tenant.atlassian.net/wiki",
  "session_token": "eyJ...",
  "diagrams_dir": "diagrams",
  "base_dir": ".",
  "pages": [
    {
      "md_file": "01-pipeline-model.md",
      "page_id": "2277408796",
      "title": "Pipeline Model",
      "diagrams": ["03-outbound-pipeline.drawio"]
    }
  ]
}
```

### Authentication

Uses `tenant.session.token` cookie (JWT) from browser. Extract via DevTools or playwright-cli. Re-extract if you get 401.

### Key storage format elements

- **Status badges**: `<ac:structured-macro ac:name="status">` (Blue/Green/Yellow/Red)
- **Draw.io**: `<ac:structured-macro ac:name="drawio">` with `custContentId` referencing uploaded attachment
- **Two-column**: `<ac:layout-section ac:type="two_equal">`
- **Code**: `<ac:structured-macro ac:name="code">` with CDATA body
- **Note**: `<ac:structured-macro ac:name="note">` from blockquotes

Full API reference: [references/confluence-storage.md](references/confluence-storage.md)

---

## Pitfalls Quick Reference

| # | Pitfall | Fix |
|---|---------|-----|
| 1 | `d.setId` crash (ID collisions) | Use `write_diagram()` for ID prefixing |
| 2 | `d.setId` crash (ER markers) | Use `classic`/`oval` arrows |
| 3 | JSON parse errors in HTML | Use URL-based draw.io loading |
| 4 | Diagrams never render | Serve via HTTP, not file:// |
| 5 | Raw HTML in draw.io cells | Add `html=1;` to style |
| 6 | Confluence 409 conflict | GET version, increment by 1 |
| 7 | CDATA breaks in Confluence | Escape `]]>` as `]]]]><![CDATA[>` |
| 8 | Draw.io "not found" in Confluence | Upload attachment before page update |
| 9 | Confluence 401/403 | Re-extract cookie; add X-Atlassian-Token header |
| 10 | Two-column cramped | Only for tall diagrams + short bullets |

Full details with symptoms and causes: [references/pitfalls.md](references/pitfalls.md)

---

## Project Template

```
my-docs/
  00-overview.md ... NN-topic.md     # Markdown sources
  diagrams/
    generate.py                       # Your diagram generator
    drawio_helpers.py                 # Copy from plugin scripts/
    *.drawio                          # Generated diagrams
  html/
    render_html.py                    # Copy from plugin scripts/
    *.html                            # Generated output
    *.drawio                          # Copied for viewer
  confluence.json                     # Page mapping (optional)
```

## Reference Files

| File | When to read |
|------|-------------|
| [references/markdown-conventions.md](references/markdown-conventions.md) | Writing or reviewing documents |
| [references/drawio-format.md](references/drawio-format.md) | Draw.io XML structure, CLI export, style properties |
| [references/confluence-storage.md](references/confluence-storage.md) | Publishing to Confluence, debugging storage format |
| [references/pitfalls.md](references/pitfalls.md) | Debugging any pipeline issue |
