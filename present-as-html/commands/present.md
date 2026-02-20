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
- Diagrams are authored as Mermaid source, rendered to SVG via `@mermaid-js/mermaid-cli`, and embedded directly as inline `<svg>` elements (see Step 6)
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

Follow this exact structure. The complete CSS and JavaScript are provided below — use them as-is, then fill in the content sections. Diagrams are pre-rendered to inline SVGs before writing the HTML (see Step 6).

### Step 1: HTML Head + Styles

```html
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>DOCUMENT_TITLE</title>
```

### Step 2: CSS

Use this complete stylesheet. Do NOT modify the core styles — only add new classes if the content requires it.

```html
<style>
  :root {
    --bg: #fafafa; --sidebar-bg: #1e293b; --sidebar-text: #cbd5e1; --sidebar-heading: #f8fafc;
    --sidebar-active: #38bdf8; --sidebar-hover: #334155; --content-bg: #ffffff; --text: #1e293b;
    --text-muted: #64748b; --heading: #0f172a; --accent: #2563eb; --accent-light: #dbeafe;
    --border: #e2e8f0; --code-bg: #f1f5f9;
    --tag-green: #dcfce7; --tag-green-text: #166534; --tag-blue: #dbeafe; --tag-blue-text: #1e40af;
    --tag-amber: #fef3c7; --tag-amber-text: #92400e; --tag-purple: #f3e8ff; --tag-purple-text: #6b21a8;
    --shadow: 0 1px 3px rgba(0,0,0,.08), 0 1px 2px rgba(0,0,0,.04);
    --right-panel-width: 420px;
    --bottom-panel-height: 320px;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  html { scroll-behavior:smooth; scroll-padding-top:24px; }
  body { font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Inter,Roboto,sans-serif; background:var(--bg); color:var(--text); line-height:1.65; font-size:15px; }

  /* Sidebar */
  .sidebar { position:fixed; top:0; left:0; width:280px; height:100vh; background:var(--sidebar-bg); color:var(--sidebar-text); overflow-y:auto; z-index:100; display:flex; flex-direction:column; border-right:1px solid rgba(255,255,255,.06); }
  .sidebar-header { padding:28px 24px 20px; border-bottom:1px solid rgba(255,255,255,.08); }
  .sidebar-header h1 { font-size:15px; font-weight:700; color:var(--sidebar-heading); margin-bottom:2px; }
  .sidebar-header .subtitle { font-size:12px; color:var(--sidebar-text); opacity:.7; }
  .sidebar nav { padding:16px 0; flex:1; }
  .sidebar nav a { display:block; padding:7px 24px; color:var(--sidebar-text); text-decoration:none; font-size:13px; transition:all .15s; border-left:3px solid transparent; }
  .sidebar nav a:hover { background:var(--sidebar-hover); color:var(--sidebar-heading); }
  .sidebar nav a.active { color:var(--sidebar-active); border-left-color:var(--sidebar-active); background:rgba(56,189,248,.06); font-weight:500; }
  .sidebar nav .nav-section { font-size:10px; font-weight:700; text-transform:uppercase; letter-spacing:.08em; color:var(--sidebar-text); opacity:.5; padding:18px 24px 6px; }
  .sidebar-footer { padding:16px 24px; border-top:1px solid rgba(255,255,255,.08); font-size:11px; opacity:.5; }
  .sidebar::-webkit-scrollbar { width:6px; }
  .sidebar::-webkit-scrollbar-thumb { background:rgba(255,255,255,.15); border-radius:3px; }

  /* App Grid Layout (wraps main + panels) */
  #appGrid {
    margin-left: 280px;
    display: grid;
    grid-template-columns: 1fr 0px;
    grid-template-rows: 1fr 0px;
    grid-template-areas:
      "content right"
      "bottom  bottom";
    height: 100vh;
    overflow: hidden;
  }
  #appGrid.right-open { grid-template-columns: 1fr var(--right-panel-width); }
  #appGrid.bottom-open { grid-template-rows: 1fr var(--bottom-panel-height); }
  #appGrid.right-open.bottom-open { grid-template-columns: 1fr var(--right-panel-width); grid-template-rows: 1fr var(--bottom-panel-height); }

  /* Main content */
  .main { grid-area: content; overflow-y: auto; padding:40px 60px 80px; max-width:none; scroll-padding-top:24px; }

  /* Tags */
  .doc-meta { display:flex; gap:12px; flex-wrap:wrap; margin-bottom:32px; }
  .tag { display:inline-flex; align-items:center; padding:3px 10px; border-radius:6px; font-size:12px; font-weight:600; }
  .tag-blue { background:var(--tag-blue); color:var(--tag-blue-text); }
  .tag-green { background:var(--tag-green); color:var(--tag-green-text); }
  .tag-amber { background:var(--tag-amber); color:var(--tag-amber-text); }
  .tag-purple { background:var(--tag-purple); color:var(--tag-purple-text); }

  /* Typography */
  h2 { font-size:22px; font-weight:700; color:var(--heading); margin:48px 0 16px; padding-bottom:10px; border-bottom:2px solid var(--border); letter-spacing:-.02em; }
  h2:first-of-type { margin-top:0; }
  h3 { font-size:16px; font-weight:650; color:var(--heading); margin:32px 0 12px; }
  h4 { font-size:14px; font-weight:650; color:var(--text-muted); text-transform:uppercase; letter-spacing:.04em; margin:24px 0 10px; }
  p { margin-bottom:14px; }
  strong { font-weight:650; }
  em { font-style:italic; color:var(--text-muted); }
  a { color:var(--accent); text-decoration:none; }
  code { font-family:'SF Mono','JetBrains Mono',Menlo,monospace; font-size:13px; background:var(--code-bg); padding:2px 6px; border-radius:4px; color:#c2410c; }
  ul, ol { margin:10px 0 14px 22px; }
  li { margin-bottom:5px; }
  li strong { color:var(--heading); }

  /* Cards & Callouts */
  .card { background:var(--content-bg); border:1px solid var(--border); border-radius:10px; padding:24px; margin:16px 0; box-shadow:var(--shadow); }
  .card-accent { border-left:4px solid var(--accent); }
  .callout { background:var(--accent-light); border-left:4px solid var(--accent); border-radius:0 8px 8px 0; padding:16px 20px; margin:20px 0; font-size:14px; }
  .callout strong { color:var(--accent); }

  /* Tables */
  table { width:100%; border-collapse:collapse; margin:16px 0; font-size:13.5px; }
  thead th { background:var(--code-bg); font-weight:650; text-align:left; padding:10px 14px; border-bottom:2px solid var(--border); color:var(--heading); font-size:12px; text-transform:uppercase; letter-spacing:.04em; }
  tbody td { padding:9px 14px; border-bottom:1px solid var(--border); vertical-align:top; }
  tbody tr:hover { background:rgba(37,99,235,.03); }

  /* Stats dashboard */
  .stats { display:grid; grid-template-columns:repeat(auto-fit,minmax(170px,1fr)); gap:14px; margin:20px 0; }
  .stat { background:var(--content-bg); border:1px solid var(--border); border-radius:10px; padding:18px 20px; box-shadow:var(--shadow); text-align:center; }
  .stat .num { font-size:28px; font-weight:800; color:var(--accent); letter-spacing:-.03em; }
  .stat .label { font-size:12px; color:var(--text-muted); margin-top:2px; font-weight:500; }

  /* Diagram containers */
  .diagram-container { background:var(--content-bg); border:1px solid var(--border); border-radius:10px; padding:24px; margin:20px 0; box-shadow:var(--shadow); overflow-x:auto; position:relative; }
  .diagram-container .mermaid { display:flex; justify-content:center; }

  /* Expand button + popover (replaces old fullscreen-btn) */
  .expand-btn-wrapper { position:absolute; top:10px; right:10px; z-index:2; }
  .diagram-container .expand-btn { width:34px; height:34px; border:1px solid var(--border); border-radius:7px; background:var(--content-bg); color:var(--text-muted); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:16px; transition:all .15s; box-shadow:var(--shadow); }
  .diagram-container .expand-btn:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
  .expand-popover { position:absolute; top:100%; right:0; margin-top:4px; background:var(--content-bg); border:1px solid var(--border); border-radius:8px; box-shadow:0 4px 16px rgba(0,0,0,0.12); padding:4px; z-index:50; display:none; min-width:150px; }
  .expand-popover.active { display:block; }
  .expand-popover button { display:flex; align-items:center; gap:8px; width:100%; padding:8px 12px; border:none; border-radius:6px; background:transparent; color:var(--text); font-size:13px; cursor:pointer; transition:background 0.1s; text-align:left; }
  .expand-popover button:hover { background:var(--accent-light); color:var(--accent); }
  .expand-popover .pop-icon { width:20px; text-align:center; font-size:15px; }

  /* Fullscreen overlay */
  .diagram-overlay { position:fixed; inset:0; z-index:9999; background:rgba(15,23,42,.85); backdrop-filter:blur(6px); display:none; flex-direction:column; align-items:center; justify-content:center; }
  .diagram-overlay.active { display:flex; }
  .diagram-overlay-toolbar { position:absolute; top:16px; right:16px; display:flex; gap:8px; z-index:10001; }
  .diagram-overlay-toolbar button { width:40px; height:40px; border:1px solid rgba(255,255,255,.2); border-radius:8px; background:rgba(30,41,59,.9); color:#e2e8f0; cursor:pointer; font-size:18px; display:flex; align-items:center; justify-content:center; transition:all .15s; }
  .diagram-overlay-toolbar button:hover { background:var(--accent); color:#fff; border-color:var(--accent); }
  .diagram-overlay-hint { position:absolute; bottom:20px; left:50%; transform:translateX(-50%); color:rgba(255,255,255,.45); font-size:12px; pointer-events:none; z-index:10001; }
  .diagram-overlay-viewport { width:100%; height:100%; overflow:hidden; cursor:grab; }
  .diagram-overlay-viewport.grabbing { cursor:grabbing; }
  .diagram-overlay-viewport .diagram-inner { transform-origin:0 0; display:flex; align-items:center; justify-content:center; min-width:100%; min-height:100%; }

  /* Right Panel */
  .right-panel { grid-area:right; display:none; flex-direction:column; border-left:2px solid var(--border); background:var(--bg); position:relative; overflow:hidden; min-width:0; }
  #appGrid.right-open .right-panel { display:flex; }

  /* Bottom Panel */
  .bottom-panel { grid-area:bottom; display:none; flex-direction:column; border-top:2px solid var(--border); background:var(--bg); position:relative; overflow:hidden; min-height:0; }
  #appGrid.bottom-open .bottom-panel { display:flex; }

  /* Panel Toolbar */
  .panel-toolbar { display:flex; align-items:center; gap:6px; padding:8px 12px; background:var(--content-bg); border-bottom:1px solid var(--border); flex-shrink:0; font-size:13px; color:var(--text-muted); }
  .panel-toolbar .panel-title { flex:1; font-weight:600; color:var(--heading); font-size:12px; text-transform:uppercase; letter-spacing:0.04em; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  .panel-toolbar button { width:30px; height:30px; border:1px solid var(--border); border-radius:6px; background:var(--content-bg); color:var(--text-muted); cursor:pointer; display:flex; align-items:center; justify-content:center; font-size:15px; transition:all 0.15s; }
  .panel-toolbar button:hover { background:var(--accent); color:#fff; border-color:var(--accent); }

  /* Panel Viewport */
  .panel-viewport { flex:1; overflow:hidden; cursor:grab; position:relative; }
  .panel-viewport.grabbing { cursor:grabbing; }
  .panel-viewport .diagram-inner { transform-origin:0 0; display:flex; align-items:center; justify-content:center; min-width:100%; min-height:100%; }

  /* Resize Handles */
  .resize-handle-v { position:absolute; top:0; left:-4px; width:8px; height:100%; cursor:col-resize; z-index:10; background:transparent; }
  .resize-handle-v::after { content:''; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:4px; height:40px; border-radius:2px; background:var(--border); transition:background 0.15s; }
  .resize-handle-v:hover::after, .resize-handle-v.active::after { background:var(--accent); }
  .resize-handle-h { position:absolute; top:-4px; left:0; width:100%; height:8px; cursor:row-resize; z-index:10; background:transparent; }
  .resize-handle-h::after { content:''; position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); width:40px; height:4px; border-radius:2px; background:var(--border); transition:background 0.15s; }
  .resize-handle-h:hover::after, .resize-handle-h.active::after { background:var(--accent); }

  /* Summary grid */
  .summary-grid { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin:20px 0; }
  .summary-item { display:flex; gap:12px; padding:14px 16px; background:var(--content-bg); border:1px solid var(--border); border-radius:8px; box-shadow:var(--shadow); }
  .summary-item .icon { width:32px; height:32px; border-radius:8px; display:flex; align-items:center; justify-content:center; font-size:16px; flex-shrink:0; }
  .summary-item .icon.blue { background:var(--tag-blue); }
  .summary-item .icon.green { background:var(--tag-green); }
  .summary-item .icon.amber { background:var(--tag-amber); }
  .summary-item .icon.purple { background:var(--tag-purple); }
  .summary-item .text .title { font-weight:650; font-size:13px; color:var(--heading); }
  .summary-item .text .desc { font-size:12px; color:var(--text-muted); margin-top:2px; }

  /* Scope badges (optional, for domain-tagged content) */
  .scope-badge { display:inline-block; background:var(--tag-blue); color:var(--tag-blue-text); padding:1px 7px; border-radius:4px; font-size:11px; font-weight:600; margin-right:4px; }

  /* Responsive */
  @media (max-width:900px) { .sidebar{display:none} #appGrid{margin-left:0} .main{padding:24px 20px 60px} .summary-grid{grid-template-columns:1fr} .right-panel,.bottom-panel{display:none !important} }
</style>
</head>
```

### Step 3: Sidebar Structure

```html
<body>
<aside class="sidebar">
  <div class="sidebar-header">
    <h1>DOCUMENT_TITLE</h1>
    <div class="subtitle">SUBTITLE</div>
  </div>
  <nav>
    <div class="nav-section">SECTION_GROUP_1</div>
    <a href="#section-id">Section Name</a>
    <a href="#section-id-2">Section Name 2</a>
    <div class="nav-section">SECTION_GROUP_2</div>
    <a href="#section-id-3">Section Name 3</a>
    <!-- ... more sections ... -->
  </nav>
  <div class="sidebar-footer">DATE &middot; AUTHOR<br>Generated with AI assistance</div>
</aside>
```

### Step 4: Main Content Area (with App Grid and Panels)

Wrap `<main>` and the panel elements inside `<div id="appGrid">`. The grid manages the content area, right panel, and bottom panel.

```html
<div id="appGrid">
<main class="main">
  <!-- Optional: document meta tags -->
  <div class="doc-meta">
    <span class="tag tag-blue">Tag 1</span>
    <span class="tag tag-green">Tag 2</span>
    <span class="tag tag-amber">Tag 3</span>
  </div>

  <!-- Sections with IDs matching sidebar links -->
  <h2 id="section-id">1. Section Title</h2>
  <p>Content here...</p>

  <!-- Use components as needed (see Component Reference below) -->
</main>

<!-- Right Panel -->
<aside class="right-panel" id="rightPanel">
  <div class="resize-handle-v" id="resizeRight"></div>
  <div class="panel-toolbar">
    <span class="panel-title" id="rightPanelTitle">Diagram</span>
    <button id="rightZoomIn" title="Zoom in">+</button>
    <button id="rightZoomOut" title="Zoom out">&minus;</button>
    <button id="rightZoomReset" title="Reset zoom">1:1</button>
    <button id="rightClose" title="Close panel">&times;</button>
  </div>
  <div class="panel-viewport" id="rightViewport">
    <div class="diagram-inner" id="rightInner"></div>
  </div>
</aside>

<!-- Bottom Panel -->
<aside class="bottom-panel" id="bottomPanel">
  <div class="resize-handle-h" id="resizeBottom"></div>
  <div class="panel-toolbar">
    <span class="panel-title" id="bottomPanelTitle">Diagram</span>
    <button id="bottomZoomIn" title="Zoom in">+</button>
    <button id="bottomZoomOut" title="Zoom out">&minus;</button>
    <button id="bottomZoomReset" title="Reset zoom">1:1</button>
    <button id="bottomClose" title="Close panel">&times;</button>
  </div>
  <div class="panel-viewport" id="bottomViewport">
    <div class="diagram-inner" id="bottomInner"></div>
  </div>
</aside>
</div><!-- /appGrid -->
```

### Step 5: Fullscreen Overlay + JavaScript

Place the fullscreen overlay HTML **after** the closing `</div><!-- /appGrid -->` and before the `<script>` tag. Use exactly as-is — do not modify.

```html
<!-- Fullscreen overlay (outside appGrid, fixed position) -->
<div class="diagram-overlay" id="diagramOverlay">
  <div class="diagram-overlay-toolbar">
    <button id="zoomIn" title="Zoom in">+</button>
    <button id="zoomOut" title="Zoom out">&minus;</button>
    <button id="zoomReset" title="Reset zoom">1:1</button>
    <button id="overlayClose" title="Close (Esc)">&times;</button>
  </div>
  <div class="diagram-overlay-viewport" id="overlayViewport">
    <div class="diagram-inner" id="overlayInner"></div>
  </div>
  <div class="diagram-overlay-hint">Scroll to zoom &middot; Drag to pan &middot; Esc to close</div>
</div>

<script>
(function(){
  /* ── Panel State ── */
  var panelState = {
    right: { open:false, sourceContainer:null, scale:1, tx:0, ty:0, dragging:false, dragStartX:0, dragStartY:0, dragTxStart:0, dragTyStart:0 },
    bottom: { open:false, sourceContainer:null, scale:1, tx:0, ty:0, dragging:false, dragStartX:0, dragStartY:0, dragTxStart:0, dragTyStart:0 }
  };

  var appGrid = document.getElementById('appGrid');
  var mainEl = document.querySelector('.main');

  /* ── Scroll-spy (uses .main as scroll container) ── */
  var links = document.querySelectorAll('.sidebar nav a[href^="#"]');
  var sections = [];
  links.forEach(function(l) {
    var id = l.getAttribute('href').slice(1);
    var el = document.getElementById(id);
    if (el) sections.push({ el:el, link:l });
  });

  function onScroll() {
    var y = mainEl.scrollTop + 80;
    var cur = sections[0];
    for (var i = 0; i < sections.length; i++) {
      if (sections[i].el.offsetTop <= y) cur = sections[i];
    }
    links.forEach(function(l) { l.classList.remove('active'); });
    if (cur) cur.link.classList.add('active');
  }
  mainEl.addEventListener('scroll', onScroll, { passive:true });
  onScroll();

  /* ── Sidebar nav click handling (scroll within .main) ── */
  links.forEach(function(l) {
    l.addEventListener('click', function(e) {
      e.preventDefault();
      var id = l.getAttribute('href').slice(1);
      var target = document.getElementById(id);
      if (target) {
        mainEl.scrollTo({ top: target.offsetTop - 24, behavior: 'smooth' });
      }
    });
  });

  /* ── Popover logic ── */
  function closeAllPopovers() {
    document.querySelectorAll('.expand-popover.active').forEach(function(p) { p.classList.remove('active'); });
  }
  document.addEventListener('click', closeAllPopovers);

  /* ── Expand button + popover per diagram ── */
  document.querySelectorAll('.diagram-container').forEach(function(container) {
    var wrapper = document.createElement('div');
    wrapper.className = 'expand-btn-wrapper';

    var btn = document.createElement('button');
    btn.className = 'expand-btn';
    btn.title = 'Expand diagram';
    btn.innerHTML = '&#x26F6;';

    var popover = document.createElement('div');
    popover.className = 'expand-popover';
    popover.innerHTML =
      '<button data-mode="fullscreen"><span class="pop-icon">&#x26F6;</span> Fullscreen</button>' +
      '<button data-mode="right"><span class="pop-icon">&#x25D0;</span> Right panel</button>' +
      '<button data-mode="bottom"><span class="pop-icon">&#x2584;</span> Bottom panel</button>';

    wrapper.appendChild(btn);
    wrapper.appendChild(popover);
    container.appendChild(wrapper);

    btn.addEventListener('click', function(e) {
      e.stopPropagation();
      var wasActive = popover.classList.contains('active');
      closeAllPopovers();
      if (!wasActive) popover.classList.add('active');
    });

    popover.addEventListener('click', function(e) {
      var option = e.target.closest('[data-mode]');
      if (!option) return;
      e.stopPropagation();
      popover.classList.remove('active');
      var mode = option.dataset.mode;
      if (mode === 'fullscreen') openOverlay(container);
      else if (mode === 'right') openPanel('right', container);
      else if (mode === 'bottom') openPanel('bottom', container);
    });
  });

  /* ── Panel open/close ── */
  function findNearestHeading(container) {
    var el = container.previousElementSibling;
    while (el) {
      if (el.tagName === 'H2' || el.tagName === 'H3') return el.textContent;
      el = el.previousElementSibling;
    }
    return null;
  }

  function applyPanelTransform(which) {
    var state = panelState[which];
    var inner = document.getElementById(which === 'right' ? 'rightInner' : 'bottomInner');
    inner.style.transform = 'translate(' + state.tx + 'px,' + state.ty + 'px) scale(' + state.scale + ')';
  }

  function openPanel(which, container) {
    var state = panelState[which];
    var innerEl = document.getElementById(which === 'right' ? 'rightInner' : 'bottomInner');
    var titleEl = document.getElementById(which === 'right' ? 'rightPanelTitle' : 'bottomPanelTitle');

    var svg = container.querySelector('svg');
    if (!svg) return;
    var clone = svg.cloneNode(true);
    clone.removeAttribute('width');
    clone.removeAttribute('height');
    clone.style.maxWidth = 'none';
    clone.style.maxHeight = 'none';
    clone.style.width = 'auto';
    clone.style.height = 'auto';

    innerEl.innerHTML = '';
    innerEl.appendChild(clone);

    state.scale = 1; state.tx = 0; state.ty = 0;
    state.sourceContainer = container;
    applyPanelTransform(which);

    var heading = findNearestHeading(container);
    titleEl.textContent = heading || 'Diagram';

    state.open = true;
    appGrid.classList.add(which + '-open');
  }

  function closePanel(which) {
    var state = panelState[which];
    var innerEl = document.getElementById(which === 'right' ? 'rightInner' : 'bottomInner');

    state.open = false;
    state.sourceContainer = null;
    appGrid.classList.remove(which + '-open');
    innerEl.innerHTML = '';
  }

  /* ── Per-panel zoom/pan ── */
  function setupPanelZoomPan(which) {
    var state = panelState[which];
    var prefix = which === 'right' ? 'right' : 'bottom';
    var viewport = document.getElementById(prefix + 'Viewport');

    document.getElementById(prefix + 'ZoomIn').addEventListener('click', function() {
      state.scale = Math.min(state.scale * 1.3, 8);
      applyPanelTransform(which);
    });
    document.getElementById(prefix + 'ZoomOut').addEventListener('click', function() {
      state.scale = Math.max(state.scale / 1.3, 0.2);
      applyPanelTransform(which);
    });
    document.getElementById(prefix + 'ZoomReset').addEventListener('click', function() {
      state.scale = 1; state.tx = 0; state.ty = 0;
      applyPanelTransform(which);
    });
    document.getElementById(prefix + 'Close').addEventListener('click', function() {
      closePanel(which);
    });

    viewport.addEventListener('wheel', function(e) {
      e.preventDefault();
      var rect = viewport.getBoundingClientRect();
      var mx = e.clientX - rect.left;
      var my = e.clientY - rect.top;
      var factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
      var newScale = Math.min(Math.max(state.scale * factor, 0.2), 8);
      state.tx = mx - (mx - state.tx) * (newScale / state.scale);
      state.ty = my - (my - state.ty) * (newScale / state.scale);
      state.scale = newScale;
      applyPanelTransform(which);
    }, { passive:false });

    viewport.addEventListener('mousedown', function(e) {
      if (e.target.closest('button')) return;
      state.dragging = true;
      state.dragStartX = e.clientX;
      state.dragStartY = e.clientY;
      state.dragTxStart = state.tx;
      state.dragTyStart = state.ty;
      viewport.classList.add('grabbing');
    });

    window.addEventListener('mousemove', function(e) {
      if (!state.dragging) return;
      state.tx = state.dragTxStart + (e.clientX - state.dragStartX);
      state.ty = state.dragTyStart + (e.clientY - state.dragStartY);
      applyPanelTransform(which);
    });

    window.addEventListener('mouseup', function() {
      if (state.dragging) {
        state.dragging = false;
        viewport.classList.remove('grabbing');
      }
    });
  }

  setupPanelZoomPan('right');
  setupPanelZoomPan('bottom');

  /* ── Resize handles ── */
  function setupResize(handleId, which) {
    var handle = document.getElementById(handleId);
    var startPos = 0;
    var startSize = 0;

    handle.addEventListener('mousedown', function(e) {
      e.preventDefault();
      handle.classList.add('active');

      if (which === 'right') {
        startPos = e.clientX;
        startSize = document.getElementById('rightPanel').getBoundingClientRect().width;
      } else {
        startPos = e.clientY;
        startSize = document.getElementById('bottomPanel').getBoundingClientRect().height;
      }

      function onMove(e) {
        if (which === 'right') {
          var delta = startPos - e.clientX;
          var newSize = Math.min(Math.max(startSize + delta, 250), window.innerWidth - 400);
          appGrid.style.setProperty('--right-panel-width', newSize + 'px');
        } else {
          var delta = startPos - e.clientY;
          var newSize = Math.min(Math.max(startSize + delta, 150), window.innerHeight - 200);
          appGrid.style.setProperty('--bottom-panel-height', newSize + 'px');
        }
      }

      function onUp() {
        handle.classList.remove('active');
        window.removeEventListener('mousemove', onMove);
        window.removeEventListener('mouseup', onUp);
      }

      window.addEventListener('mousemove', onMove);
      window.addEventListener('mouseup', onUp);
    });
  }

  setupResize('resizeRight', 'right');
  setupResize('resizeBottom', 'bottom');

  /* ── Fullscreen Overlay ── */
  var overlay = document.getElementById('diagramOverlay');
  var viewport = document.getElementById('overlayViewport');
  var inner = document.getElementById('overlayInner');
  var scale = 1, tx = 0, ty = 0, dragging = false, dragStartX = 0, dragStartY = 0, dragTxStart = 0, dragTyStart = 0;

  function applyTransform() { inner.style.transform = 'translate(' + tx + 'px,' + ty + 'px) scale(' + scale + ')'; }

  function openOverlay(container) {
    var svg = container.querySelector('svg');
    if (!svg) return;
    var clone = svg.cloneNode(true);
    clone.removeAttribute('width'); clone.removeAttribute('height');
    clone.style.maxWidth = 'none'; clone.style.maxHeight = 'none';
    clone.style.width = 'auto'; clone.style.height = 'auto';
    inner.innerHTML = '';
    inner.appendChild(clone);
    scale = 1; tx = 0; ty = 0;
    applyTransform();
    overlay.classList.add('active');
    document.body.style.overflow = 'hidden';
  }

  function closeOverlay() {
    overlay.classList.remove('active');
    document.body.style.overflow = '';
    inner.innerHTML = '';
  }

  document.getElementById('overlayClose').addEventListener('click', closeOverlay);
  overlay.addEventListener('click', function(e) { if (e.target === overlay || e.target === viewport) closeOverlay(); });

  /* ── Keyboard: Escape closes fullscreen first, then popovers ── */
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') {
      if (overlay.classList.contains('active')) {
        closeOverlay();
      } else {
        closeAllPopovers();
      }
    }
  });

  /* ── Zoom buttons ── */
  document.getElementById('zoomIn').addEventListener('click', function(e) { e.stopPropagation(); scale = Math.min(scale * 1.3, 8); applyTransform(); });
  document.getElementById('zoomOut').addEventListener('click', function(e) { e.stopPropagation(); scale = Math.max(scale / 1.3, 0.2); applyTransform(); });
  document.getElementById('zoomReset').addEventListener('click', function(e) { e.stopPropagation(); scale = 1; tx = 0; ty = 0; applyTransform(); });

  /* ── Scroll zoom ── */
  viewport.addEventListener('wheel', function(e) {
    e.preventDefault();
    var rect = viewport.getBoundingClientRect();
    var mx = e.clientX - rect.left, my = e.clientY - rect.top;
    var factor = e.deltaY < 0 ? 1.15 : 1 / 1.15;
    var newScale = Math.min(Math.max(scale * factor, 0.2), 8);
    tx = mx - (mx - tx) * (newScale / scale);
    ty = my - (my - ty) * (newScale / scale);
    scale = newScale;
    applyTransform();
  }, { passive:false });

  /* ── Drag pan ── */
  viewport.addEventListener('mousedown', function(e) {
    if (e.target.closest('button')) return;
    dragging = true; dragStartX = e.clientX; dragStartY = e.clientY;
    dragTxStart = tx; dragTyStart = ty;
    viewport.classList.add('grabbing');
  });
  window.addEventListener('mousemove', function(e) {
    if (!dragging) return;
    tx = dragTxStart + (e.clientX - dragStartX);
    ty = dragTyStart + (e.clientY - dragStartY);
    applyTransform();
  });
  window.addEventListener('mouseup', function() { if (dragging) { dragging = false; viewport.classList.remove('grabbing'); } });
})();
</script>
</body>
</html>
```

### Step 6: Pre-render Diagrams to Inline SVGs

**Before writing the HTML file**, render all Mermaid diagrams to SVG and embed them directly. This ensures the document has zero JavaScript or CDN dependencies — diagrams work on SharePoint, Teams, Confluence, email, and offline.

#### 6a. Create a Mermaid theme config

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

#### 6b. Render each diagram

For each diagram you plan to include:

1. Write the Mermaid source to a temp file (e.g. `/tmp/diagram-0.mmd`)
2. Render to SVG:
   ```bash
   npx -y @mermaid-js/mermaid-cli -i /tmp/diagram-0.mmd -o /tmp/diagram-0.svg -b transparent -c /tmp/mermaid-config.json --quiet
   ```
3. Read the generated SVG file content

Repeat for each diagram (increment the index: `diagram-1.mmd`, `diagram-2.mmd`, etc.). These can be run in parallel since they're independent.

**Note:** The first run of `npx @mermaid-js/mermaid-cli` downloads Chromium (~200 MB). This is a one-time cost — subsequent runs use the cached binary.

#### 6c. Embed in the HTML

When writing the HTML file (Steps 1–5), embed the rendered SVGs directly inside `.diagram-container` divs:

```html
<div class="diagram-container">
  <div class="mermaid" style="display:flex;justify-content:center;">
    SVG_CONTENT_HERE
  </div>
</div>
```

Do NOT use `<pre class="mermaid">` in the final HTML. Do NOT include any Mermaid CDN `<script>` tags or `mermaid.initialize()` calls — they are not needed.

#### 6d. Fallback

If `npx` is not available (no Node.js), fall back to the CDN approach:
- Add to the HTML `<head>`:
  ```html
  <script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
  <script>mermaid.initialize({ startOnLoad: true, theme: 'base', themeVariables: { primaryColor: '#dbeafe', primaryTextColor: '#1e40af', primaryBorderColor: '#2563eb', lineColor: '#64748b', secondaryColor: '#dcfce7', tertiaryColor: '#f3e8ff', fontSize: '14px' }});</script>
  ```
- Use `<pre class="mermaid">` blocks instead of inline SVGs
- Warn the user: "Diagrams require JavaScript to render. They will not display on SharePoint, Teams, or other platforms that sandbox HTML. Install Node.js to enable automatic pre-rendering."

#### 6e. Cleanup

Remove the temporary files:

```bash
rm -f /tmp/diagram-*.mmd /tmp/diagram-*.svg /tmp/mermaid-config.json
```

---

## Component Reference

Use these HTML patterns inside `<main class="main">` to build the document content.

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

Diagrams are pre-rendered to inline SVGs via Step 6. Write the Mermaid source to a `.mmd` temp file, render with `mmdc`, then embed the SVG output:

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

Panels are built into the page layout via `#appGrid`. They are **not** placed per-diagram -- there is one right panel and one bottom panel for the entire document, and diagrams are loaded into them dynamically via the popover menu. The HTML for both panels goes inside `#appGrid` after `</main>` (see Step 4 above).

Each panel contains:
- **Resize handle** (`.resize-handle-v` for right, `.resize-handle-h` for bottom) -- draggable to resize
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
2. **Pre-render Mermaid to inline SVGs** — the CDN works for local viewing, but platforms like SharePoint, Teams, and email clients block all JavaScript. Step 6 converts diagrams to inline SVGs via `@mermaid-js/mermaid-cli`, making the file truly zero-dependency.
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

---

## Error Handling

- If `npx @mermaid-js/mermaid-cli` fails on a specific diagram, check the Mermaid syntax in the corresponding `.mmd` file. Common issues: unescaped quotes in labels, invalid diagram type, mismatched brackets.
- If the SVG count after pre-rendering doesn't match the diagram count, a diagram failed to render. Check the mmdc stderr output for the failing diagram index.
- If `npx` is not available at all, the HTML falls back to CDN mode. Diagrams will work locally but not on SharePoint/Teams/email.
- If the sidebar doesn't highlight, verify that `id` attributes on `<h2>`/`<h3>` elements match the `href` values in sidebar `<a>` tags.
- For very large documents, the scroll-spy may lag — this is acceptable and rarely noticeable.
