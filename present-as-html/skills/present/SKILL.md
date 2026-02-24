---
description: "Generate a beautiful, self-contained HTML document from analysis, report, or research content. Creates polished single-file HTML with sidebar navigation, pre-rendered Mermaid diagrams (inline SVGs, no CDN dependency), fullscreen zoom, stats dashboards, styled tables, and more. Works on SharePoint, Teams, email, and offline. Use when the user wants to present findings, create a readable report, visualize an analysis, or generate an HTML version of any document. Invoked via /present-as-html:present."
---

# present-as-html

Generate beautiful, self-contained HTML documents from any content — analyses, reports, research findings, architecture overviews, evaluations. The output is a single `.html` file with no external dependencies that looks polished and is enjoyable to read.

---

## When to Use This Skill

- The user asks to "present", "visualize", or "make readable" some analysis or report
- The user wants an HTML version of a markdown document or findings
- The user asks for a "beautiful HTML", "nice report", or "readable document"
- The user invokes `/present-as-html:present`
- After completing an analysis, when the user wants to share findings with others

---

## What You Generate

A **single self-contained HTML file** with these features:

### 1. Fixed Sidebar Navigation
- Dark sidebar (left, 280px) with section links
- Scroll-spy: highlights the current section as the user scrolls
- Grouped nav sections with uppercase labels
- Footer with date and author

### 2. Mermaid.js Diagrams (Pre-rendered as Inline SVGs)
- Diagrams are authored as Mermaid source, rendered to SVG via `@mermaid-js/mermaid-cli`, and embedded directly as inline `<svg>` elements (see Step 2)
- No CDN or JavaScript dependency — diagrams work on SharePoint, Teams, Confluence, email, and offline
- Custom themed with the document color palette
- Each diagram in a styled container with rounded borders and shadow

### 3. Diagram Viewing: Panels + Fullscreen
- Every diagram gets an **expand button** (top-right corner) that opens a **popover menu** with three options: Fullscreen, Right panel, Bottom panel
- **Right panel**: resizable side panel for viewing diagrams alongside content. Opens via CSS Grid column. Has its own zoom/pan, resize handle, and toolbar.
- **Bottom panel**: resizable bottom panel for wide diagrams. Opens via CSS Grid row. Same features as right panel.
- **Fullscreen overlay**: full-viewport zoom/pan view with blurred backdrop. Close via Esc, close button, or clicking backdrop.
- Both panels can be open simultaneously. Opening a new diagram in an already-open panel replaces the content (no close/reopen needed).
- Panels are **not** closed by Escape (they are persistent working areas). Escape closes fullscreen first, then popovers.

### 4. Rich Content Components
- **Stats dashboard**: grid of metric cards (number + label)
- **Cards**: bordered containers with optional accent stripe
- **Callouts**: accent-colored info boxes for key insights
- **Tags/badges**: colored inline labels (blue, green, amber, purple)
- **Tables**: styled with hover, uppercase headers, proper spacing
- **Summary grid**: 2-column grid of icon + title + description items
- **Code**: monospace inline code with background highlight

### 5. Typography & Layout
- **3-pane CSS Grid layout**: sidebar (fixed, 280px) + `#appGrid` (grid with content area, right panel column, bottom panel row)
- System font stack (-apple-system, BlinkMacSystemFont, 'Segoe UI', Inter, Roboto)
- Monospace for code (SF Mono, JetBrains Mono, Menlo)
- Clean heading hierarchy with border separators
- Responsive: sidebar hides on mobile (<900px), panels hidden on mobile (fullscreen only)

---

## How to Build the HTML

### Step 1: Read the template and fill placeholders

Read `template.html` from this skill's directory (same directory as this SKILL.md). This template contains the complete CSS, HTML structure (sidebar, appGrid, panels, fullscreen overlay), and JavaScript. **Do not modify the CSS or JavaScript** — only fill in the placeholder markers.

Replace these placeholders in the template:

| Placeholder | Replace With |
|---|---|
| `{{DOCUMENT_TITLE}}` | Document title (appears in `<title>` tag and sidebar `<h1>`) |
| `{{SUBTITLE}}` | Short description shown under the sidebar title |
| `{{NAV_SECTIONS}}` | Sidebar navigation links — see format below |
| `{{META_TAGS}}` | `<div class="doc-meta">` with tag spans (or remove if none) |
| `{{CONTENT}}` | All document content: `<h2>`, `<h3>`, paragraphs, tables, diagrams, etc. |
| `{{DATE}}` | Generation date (e.g., "February 2026") |
| `{{AUTHOR}}` | Author or source info |

#### NAV_SECTIONS format

Generate sidebar links matching the `<h2>` headings in your content. Group them with `.nav-section` labels:

```html
<div class="nav-section">OVERVIEW</div>
<a href="#executive-summary">Executive Summary</a>
<a href="#at-a-glance">At a Glance</a>
<div class="nav-section">ARCHITECTURE</div>
<a href="#system-design">System Design</a>
<a href="#data-model">Data Model</a>
<div class="nav-section">DETAILS</div>
<a href="#component-analysis">Component Analysis</a>
<a href="#integration-points">Integration Points</a>
```

Each `href` must match an `id` attribute on a heading inside `{{CONTENT}}`.

#### META_TAGS format

Use 3-4 tags to communicate technology, maturity, source, and scope:

```html
<div class="doc-meta">
  <span class="tag tag-blue">Python / FastAPI</span>
  <span class="tag tag-green">Production</span>
  <span class="tag tag-amber">Code Analysis</span>
  <span class="tag tag-purple">Backend Only</span>
</div>
```

#### CONTENT format

Use standard HTML with the component classes defined in the template. Each major section starts with an `<h2 id="...">` matching the sidebar links. Use the components from the **Component Reference** section below to build rich content.

### Step 2: Pre-render Diagrams to Inline SVGs

**Before writing the HTML file**, render all Mermaid diagrams to SVG and embed them directly. This ensures the document has zero JavaScript or CDN dependencies — diagrams work on SharePoint, Teams, Confluence, email, and offline.

#### 2a. Create a Mermaid theme config

Write a temporary config file that matches the document's color palette:

```bash
cat > /tmp/mermaid-config.json << 'EOF'
{
  "theme": "base",
  "themeVariables": {
    "primaryColor": "#dbeafe",
    "primaryTextColor": "#1e40af",
    "primaryBorderColor": "#2563eb",
    "lineColor": "#64748b",
    "secondaryColor": "#dcfce7",
    "tertiaryColor": "#f3e8ff",
    "fontSize": "14px"
  }
}
EOF
```

#### 2b. Render each diagram

For each diagram you plan to include:

1. Write the Mermaid source to a temp file (e.g. `/tmp/diagram-0.mmd`)
2. Render to SVG:
   ```bash
   npx -y @mermaid-js/mermaid-cli -i /tmp/diagram-0.mmd -o /tmp/diagram-0.svg -b transparent -c /tmp/mermaid-config.json --quiet
   ```
3. Read the generated SVG file content

Repeat for each diagram (increment the index: `diagram-1.mmd`, `diagram-2.mmd`, etc.). These can be run in parallel since they're independent.

**Note:** The first run of `npx @mermaid-js/mermaid-cli` downloads Chromium (~200 MB). This is a one-time cost — subsequent runs use the cached binary.

#### 2c. Embed in the HTML

When filling `{{CONTENT}}`, embed the rendered SVGs inside `.diagram-container` divs:

```html
<div class="diagram-container">
  <div class="mermaid" style="display:flex;justify-content:center;">
    SVG_CONTENT_HERE
  </div>
</div>
```

Do NOT use `<pre class="mermaid">` in the final HTML. Do NOT include any Mermaid CDN `<script>` tags or `mermaid.initialize()` calls — they are not needed.

#### 2d. Fallback

If `npx` is not available (no Node.js), fall back to the CDN approach:
- Add to the HTML `<head>`:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({ startOnLoad: true, theme: 'base', themeVariables: { primaryColor: '#dbeafe', primaryTextColor: '#1e40af', primaryBorderColor: '#2563eb', lineColor: '#64748b', secondaryColor: '#dcfce7', tertiaryColor: '#f3e8ff', fontSize: '14px' }});</script>
  ```
- Use `<pre class="mermaid">` blocks instead of inline SVGs
- Warn the user: "Diagrams require JavaScript to render. They will not display on SharePoint, Teams, or other platforms that sandbox HTML. Install Node.js to enable automatic pre-rendering."

#### 2e. Cleanup

Remove the temporary files:

```bash
rm -f /tmp/diagram-*.mmd /tmp/diagram-*.svg /tmp/mermaid-config.json
```

### Step 3: Write the output file

Write the completed HTML (template with all placeholders filled and SVGs embedded) to the output path.

---

## Component Reference

Use these HTML patterns inside `{{CONTENT}}` to build the document.

### Stats Dashboard

Use for key metrics at the top of a section.

```html
<div class="stats">
  <div class="stat"><div class="num">42</div><div class="label">Total Items</div></div>
  <div class="stat"><div class="num">7</div><div class="label">Categories</div></div>
  <div class="stat"><div class="num">99%</div><div class="label">Coverage</div></div>
</div>
```

### Card (with optional accent border)

Use for key definitions, important context, or highlighted content blocks.

```html
<div class="card card-accent">
  <p>Important content with a <strong>blue accent stripe</strong> on the left.</p>
</div>
```

### Callout

Use for key insights, important notes, or design principles.

```html
<div class="callout">
  <strong>Key insight:</strong> This is an important takeaway that should stand out.
</div>
```

### Tags / Badges

Use inline for status indicators, categories, or labels.

```html
<span class="tag tag-green" style="font-size:11px">Active</span>
<span class="tag tag-amber" style="font-size:11px">Pending</span>
<span class="tag tag-blue" style="font-size:11px">Info</span>
<span class="tag tag-purple" style="font-size:11px">Beta</span>
```

### Styled Table

```html
<table>
  <thead><tr><th>Column 1</th><th>Column 2</th><th>Column 3</th></tr></thead>
  <tbody>
    <tr><td><strong>Row 1</strong></td><td>Value</td><td>Description</td></tr>
    <tr><td><strong>Row 2</strong></td><td>Value</td><td>Description</td></tr>
  </tbody>
</table>
```

### Mermaid Diagram

Always wrap in a `.diagram-container`. The expand button and popover are auto-injected by the JavaScript.

Diagrams are pre-rendered to inline SVGs via Step 2. Write the Mermaid source to a `.mmd` temp file, render with `mmdc`, then embed the SVG output:

```html
<div class="diagram-container">
  <div class="mermaid" style="display:flex;justify-content:center;">
    <svg><!-- rendered SVG content from mmdc --></svg>
  </div>
</div>
```

The Mermaid source for the diagram above would be:

```
graph TD
    A["Node A"] --> B["Node B"]
    B --> C["Node C"]
    style A fill:#dbeafe,stroke:#2563eb,color:#1e40af
    style B fill:#dcfce7,stroke:#16a34a,color:#166534
```

See the **Mermaid Diagram Guide** section below for syntax, diagram types, and styling.

### Diagram Panels (Right / Bottom)

Panels are built into the template layout via `#appGrid`. They are **not** placed per-diagram — there is one right panel and one bottom panel for the entire document, and diagrams are loaded into them dynamically via the popover menu. The panel HTML is already in `template.html`.

Each panel contains:
- **Resize handle** (`.resize-handle-v` for right, `.resize-handle-h` for bottom) — draggable to resize
- **Toolbar** (`.panel-toolbar`) with title, zoom in/out/reset, and close buttons
- **Viewport** (`.panel-viewport`) with a `.diagram-inner` div for the cloned SVG

**When to use panels vs fullscreen:**
- Use **right panel** when you want to read content and reference a diagram side-by-side
- Use **bottom panel** for wide diagrams (flowcharts LR, ER diagrams) where horizontal space helps
- Use **fullscreen** for maximum detail on complex diagrams

**Resize constraints:**
| Panel | Min | Max | Default |
|-------|-----|-----|---------|
| Right | 250px width | `window.innerWidth - 400` | 420px (`--right-panel-width`) |
| Bottom | 150px height | `window.innerHeight - 200` | 320px (`--bottom-panel-height`) |

### Expand Popover

The expand popover is **auto-generated by JavaScript** for every `.diagram-container`. You do NOT write popover HTML manually. The JS creates an `.expand-btn-wrapper` with the expand button and a 3-option popover (Fullscreen, Right panel, Bottom panel).

The popover dismisses on: clicking outside, clicking an option, or pressing Escape. Only one popover can be open at a time.

### Summary Grid

Use for concluding sections — 2-column grid of icon + title + description.

```html
<div class="summary-grid">
  <div class="summary-item">
    <div class="icon blue">&#9881;</div>
    <div class="text">
      <div class="title">Feature Name</div>
      <div class="desc">Brief description of the feature</div>
    </div>
  </div>
  <!-- more items... -->
</div>
```

Icon color classes: `blue`, `green`, `amber`, `purple`. Use HTML entities for icons (e.g., `&#9881;` gear, `&#8645;` arrows, `&#9874;` hammer).

### Scope Badge

Use inline to tag content with domain/category references.

```html
<span class="scope-badge">Category 1.2</span> <strong>Item Name</strong>
```

---

## Mermaid Diagram Guide

Use Mermaid.js for ALL diagrams. **Never use hand-drawn SVGs** — they don't look good and are hard to maintain.

### Which Diagram Type to Use

| Content Type | Mermaid Type | Example |
|---|---|---|
| System architecture (layers, components) | `graph TB` with `subgraph` | Architecture overview with config/runtime/comms layers |
| Pipeline / flow (left to right) | `flowchart LR` | Inbound processing: Fetch -> Store -> Parse -> Post |
| Process / orchestration (top to bottom) | `flowchart TB` with `subgraph` | Job scheduling, decision trees |
| Data model / entity relationships | `erDiagram` | Database schema with field definitions and relationships |
| Class hierarchy / inheritance tree | `graph TD` | Base class -> subclasses -> concrete implementations |
| Package / module structure | `graph TD` | Root -> subpackages/submodules |
| Sequence of interactions | `sequenceDiagram` | API call flows, request/response patterns |
| State machine | `stateDiagram-v2` | Lifecycle states and transitions |
| Timeline / milestones | `timeline` | Project phases, release history |

### Styling Mermaid Nodes

Use a consistent color palette matching the document theme:

```
style NODE fill:#dbeafe,stroke:#2563eb,stroke-width:2px,color:#1e40af    (blue — primary/config)
style NODE fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#166534    (green — runtime/storage)
style NODE fill:#f3e8ff,stroke:#9333ea,stroke-width:2px,color:#6b21a8    (purple — communication/external)
style NODE fill:#fef3c7,stroke:#d97706,color:#92400e                     (amber — scheduling/logs)
style NODE fill:#fee2e2,stroke:#dc2626,color:#991b1b                     (red — critical/alerts)
style NODE fill:#f1f5f9,stroke:#94a3b8,stroke-width:1px,stroke-dasharray:5 5,color:#64748b  (gray dashed — external systems)
style NODE fill:#0f172a,stroke:#0f172a,color:#fff                        (dark — root/factory nodes)
```

### Mermaid Tips

- Use `<b>` and `<i>` inside node labels for emphasis: `NODE["<b>Title</b><br/><i>subtitle</i>"]`
- Use `<br/>` for multi-line labels
- Use `---` for solid links, `-.-` for dotted links, `-->` for arrows
- Use `subgraph NAME["<b>Display Title</b>"]` for grouped sections
- Add `direction LR` or `direction TB` inside subgraphs to control layout
- For ER diagrams, include field types: `string FieldName PK`
- Keep diagram complexity manageable — split large diagrams into multiple smaller ones
- Use `classDef` for reusable styles when many nodes share the same color

---

## Content Guidelines

### Structure
1. **Start with an overview** — what is this about, why does it matter
2. **"At a Glance" stats** — key numbers that give a quick sense of scale
3. **Architecture / design** — how it works at a high level (use diagrams)
4. **Details** — deep dives into specific areas (tables, cards, lists)
5. **Mapping / context** — how this relates to broader context
6. **Summary** — key takeaways (use summary grid)

### Writing Style
- Be concise — this is a visual document, not a wall of text
- Use **bold** for key terms on first mention
- Use `code` for technical identifiers (class names, table names, config keys)
- Use callouts for key insights or design principles
- Use tables for structured comparisons
- Use stats dashboard for key metrics
- Every section should have at least one visual element (diagram, table, stats, or card)

### Document Meta Tags
Use 3-4 tags at the top to quickly communicate:
- Technology/platform (e.g., "ABAP / RAP", "Python", "Kubernetes")
- Maturity (e.g., "Production-grade", "Draft", "Experimental")
- Source (e.g., "Code analysis", "Interview", "Documentation review")
- Scope (e.g., "C4M + C4MHO", "Backend only", "Full stack")

---

## Lessons Learned

These are hard-won insights from building these documents:

1. **Never use hand-drawn SVGs** for diagrams. They look bad and are unmaintainable. Always use Mermaid.
2. **Pre-render Mermaid to inline SVGs** — the CDN works for local viewing, but platforms like SharePoint, Teams, and email clients block all JavaScript. Step 2 converts diagrams to inline SVGs via `@mermaid-js/mermaid-cli`, making the file truly zero-dependency.
3. **Scroll-spy makes the sidebar useful** — without it, the sidebar is just a list of links.
4. **Fullscreen zoom is essential** for complex diagrams (ER diagrams, large hierarchies). Without it, users can't read the details.
5. **The blurred backdrop** on the fullscreen overlay helps focus attention on the diagram.
6. **System font stack** looks good everywhere without loading web fonts.
7. **CSS custom properties** make the color palette consistent and easy to adjust.
8. **One file, no build step** — the output should always be a single `.html` file that works by double-clicking. No npm, no bundler, no server needed.
9. **CSS Grid is essential for panels** — the `#appGrid` uses CSS Grid to manage the content area and panels. Grid template columns/rows are toggled via `.right-open` and `.bottom-open` classes. This is far simpler than absolute positioning.
10. **Scroll-spy must target `.main`** — since the content area is now a grid child with `overflow-y: auto`, scroll-spy listens on `.main` (not `window`). Sidebar nav clicks also scroll `.main` via `mainEl.scrollTo()`.
11. **Panels are persistent, not modal** — unlike fullscreen, panels stay open while the user navigates. Escape does NOT close panels (only fullscreen and popovers). This is intentional.
12. **Each panel has independent zoom/pan state** — the `panelState` object tracks scale, tx, ty, and drag state separately for right and bottom panels. Opening a new diagram in a panel resets that panel's zoom state.
13. **Popover replaces direct click-to-fullscreen** — diagrams no longer open fullscreen on click. Users must use the expand button popover to choose their viewing mode. This avoids accidental fullscreen triggers.
14. **Use the template file** — CSS, HTML structure, and JavaScript live in `template.html`. Read it, fill in the placeholders, and write the output. Never regenerate the template from memory — this ensures no features are ever dropped.

---

## Error Handling

- If `npx @mermaid-js/mermaid-cli` fails on a specific diagram, check the Mermaid syntax in the corresponding `.mmd` file. Common issues: unescaped quotes in labels, invalid diagram type, mismatched brackets.
- If the SVG count after pre-rendering doesn't match the diagram count, a diagram failed to render. Check the mmdc stderr output for the failing diagram index.
- If `npx` is not available at all, the HTML falls back to CDN mode. Diagrams will work locally but not on SharePoint/Teams/email.
- If the sidebar doesn't highlight, verify that `id` attributes on `<h2>`/`<h3>` elements match the `href` values in sidebar `<a>` tags.
- For very large documents, the scroll-spy may lag — this is acceptable and rarely noticeable.
