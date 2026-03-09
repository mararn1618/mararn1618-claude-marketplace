#!/usr/bin/env bun
/**
 * Claude Viz — Live visualization side-panel server for Claude Code.
 * Dashboard-style pages with multi-card grid layout, sidebar history navigation.
 * Single-file Bun server, zero dependencies beyond Bun.
 */

const PORT = parseInt(process.env.CLAUDE_VIZ_PORT || "7891");
const HOST = "127.0.0.1";

interface Card {
  type: "mermaid" | "kroki" | "html" | "svg" | "markdown";
  title?: string;
  content: string;
  krokiDiagramType?: string;
  krokiOutputFormat?: string;
  size: "full" | "half"; // grid placement
}

interface Page {
  id: string;
  title: string;
  cards: Card[];
  sourceFiles?: string[];
  sessionId: string;
  sessionName: string;
  timestamp: number;
}

const pages: Page[] = [];
const sessionNames = new Map<string, string>();
const sseClients = new Set<ReadableStreamDefaultController>();

function broadcast(event: string, data: any) {
  const msg = event === "message"
    ? `data: ${JSON.stringify(data)}\n\n`
    : `event: ${event}\ndata: ${JSON.stringify(data)}\n\n`;
  for (const controller of sseClients) {
    try { controller.enqueue(msg); } catch { sseClients.delete(controller); }
  }
}

function generateId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 6);
}

const HTML_PAGE = `<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Claude Viz</title>
<style>
  :root {
    --bg: #0d1117; --bg-card: #161b22; --bg-card-hover: #1c2333;
    --bg-sidebar: #0d1117; --bg-sidebar-item: #161b22; --bg-sidebar-active: #1c2333;
    --border: #30363d; --border-highlight: #58a6ff;
    --text: #e6edf3; --text-muted: #8b949e; --text-dim: #6e7681;
    --accent: #58a6ff; --accent-soft: rgba(88,166,255,0.15);
    --green: #3fb950; --orange: #d29922; --red: #f85149; --purple: #bc8cff;
    --radius: 8px; --sidebar-w: 260px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Noto Sans', Helvetica, Arial, sans-serif;
    background: var(--bg); color: var(--text); height: 100vh; overflow: hidden;
    display: flex;
  }

  /* Sidebar */
  #sidebar {
    width: var(--sidebar-w); min-width: var(--sidebar-w); height: 100vh;
    background: var(--bg-sidebar); border-right: 1px solid var(--border);
    display: flex; flex-direction: column; overflow: hidden;
  }
  #sidebar-header {
    padding: 16px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  #sidebar-header h1 {
    font-size: 15px; font-weight: 600;
    display: flex; align-items: center; gap: 8px;
  }
  #sidebar-header .dot {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--green); animation: pulse 2s infinite;
  }
  @keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.4; } }
  #sidebar-header .clear-btn {
    background: none; border: 1px solid var(--border); color: var(--text-dim);
    padding: 3px 8px; border-radius: 4px; cursor: pointer; font-size: 11px;
  }
  #sidebar-header .clear-btn:hover { color: var(--text); border-color: var(--border-highlight); }

  /* Session filter */
  #session-filter {
    padding: 8px 12px; border-bottom: 1px solid var(--border);
    display: none; gap: 4px; flex-wrap: wrap;
  }
  #session-filter.visible { display: flex; }
  .session-pill {
    font-size: 10px; padding: 2px 8px; border-radius: 10px;
    border: 1px solid var(--border); background: var(--bg-card);
    color: var(--text-dim); cursor: pointer; transition: all 0.15s;
  }
  .session-pill:hover { color: var(--text); }
  .session-pill.active { border-color: var(--accent); color: var(--accent); background: var(--accent-soft); }

  /* Page list */
  #page-list {
    flex: 1; overflow-y: auto; padding: 8px;
  }
  #page-list::-webkit-scrollbar { width: 4px; }
  #page-list::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }
  .page-item {
    padding: 10px 12px; margin-bottom: 4px; border-radius: 6px;
    cursor: pointer; transition: all 0.15s; border: 1px solid transparent;
  }
  .page-item:hover { background: var(--bg-sidebar-item); }
  .page-item.active { background: var(--bg-sidebar-active); border-color: var(--accent); }
  .page-item.hidden-by-filter { display: none; }
  .page-item-title {
    font-size: 13px; font-weight: 500; white-space: nowrap;
    overflow: hidden; text-overflow: ellipsis;
  }
  .page-item-meta {
    font-size: 10px; color: var(--text-dim); margin-top: 3px;
    display: flex; align-items: center; gap: 6px;
  }
  .page-item-meta .card-count {
    background: var(--accent-soft); color: var(--accent);
    padding: 0 5px; border-radius: 6px;
  }
  .page-item-session-dot {
    width: 5px; height: 5px; border-radius: 50%; display: inline-block;
  }

  /* Main area */
  #main {
    flex: 1; height: 100vh; overflow-y: auto; padding: 24px 32px;
  }
  #main::-webkit-scrollbar { width: 6px; }
  #main::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }

  #page-header {
    margin-bottom: 20px; display: flex; align-items: baseline; justify-content: space-between;
  }
  #page-title { font-size: 20px; font-weight: 600; }
  #page-meta { font-size: 12px; color: var(--text-dim); }
  #page-source-files {
    margin-bottom: 16px; display: flex; flex-wrap: wrap; gap: 6px;
  }
  #page-source-files a {
    font-size: 11px; color: var(--accent); text-decoration: none;
    background: var(--accent-soft); padding: 2px 8px; border-radius: 4px;
    cursor: pointer; transition: all 0.15s;
  }
  #page-source-files a:hover { background: rgba(88,166,255,0.3); }

  /* Dashboard grid */
  #dashboard {
    display: grid; grid-template-columns: 1fr 1fr;
    gap: 16px;
  }
  .dash-card {
    background: var(--bg-card); border: 1px solid var(--border);
    border-radius: var(--radius); overflow: hidden; transition: border-color 0.15s;
  }
  .dash-card:hover { border-color: var(--border-highlight); }
  .dash-card.full { grid-column: 1 / -1; }
  .dash-card-header {
    padding: 8px 14px; border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between;
  }
  .dash-card-header-left { display: flex; align-items: center; gap: 8px; }
  .dash-card-title { font-size: 12px; font-weight: 500; color: var(--text-muted); }
  .dash-card-badge {
    font-size: 9px; font-weight: 600; text-transform: uppercase;
    padding: 1px 5px; border-radius: 3px;
  }
  .dash-card-badge.mermaid { background: rgba(63,185,80,0.15); color: var(--green); }
  .dash-card-badge.kroki { background: rgba(188,140,255,0.15); color: var(--purple); }
  .dash-card-badge.html { background: rgba(210,153,34,0.15); color: var(--orange); }
  .dash-card-badge.svg { background: var(--accent-soft); color: var(--accent); }
  .dash-card-badge.markdown { background: rgba(210,153,34,0.15); color: var(--orange); }
  .dash-card-actions button {
    background: none; border: none; color: var(--text-dim);
    cursor: pointer; padding: 2px 4px; font-size: 13px; border-radius: 3px;
  }
  .dash-card-actions button:hover { background: var(--bg-card-hover); color: var(--text); }
  .dash-card-body {
    padding: 14px; overflow-x: auto;
  }
  .dash-card-body.light-bg {
    background: #f6f8fa; border-radius: 0 0 var(--radius) var(--radius);
  }
  .dash-card-body.light-bg .markdown-container,
  .dash-card-body.light-bg .html-container { color: #1f2328; }
  .dash-card-body.light-bg .markdown-container code { background: rgba(0,0,0,0.08); color: #1f2328; }
  .dash-card-body.light-bg .markdown-container pre { background: #e6e8eb; }
  .bg-toggle {
    width: 36px; height: 18px; border-radius: 9px; border: none; padding: 0;
    background: var(--border); cursor: pointer; position: relative; transition: background 0.2s;
    display: inline-flex; align-items: center;
  }
  .bg-toggle::after {
    content: ''; position: absolute; left: 2px; top: 2px;
    width: 14px; height: 14px; border-radius: 50%;
    background: var(--text-dim); transition: all 0.2s;
  }
  .bg-toggle.light { background: var(--accent); }
  .bg-toggle.light::after { left: 20px; background: #fff; }
  .dash-card-body .mermaid-container svg { max-width: 100%; height: auto; }
  .dash-card-body .kroki-container img,
  .dash-card-body .kroki-container svg { max-width: 100%; height: auto; }
  .dash-card-body .html-container { line-height: 1.5; font-size: 14px; }
  .dash-card-body .markdown-container { line-height: 1.5; font-size: 14px; }
  .dash-card-body .markdown-container h1 { font-size: 1.4em; margin: 0 0 8px; }
  .dash-card-body .markdown-container h2 { font-size: 1.2em; margin: 12px 0 6px; color: var(--text); }
  .dash-card-body .markdown-container h3 { font-size: 1.05em; margin: 10px 0 4px; color: var(--text-muted); }
  .dash-card-body .markdown-container p { margin: 0 0 6px; }
  .dash-card-body .markdown-container ul { padding-left: 20px; margin: 4px 0 8px; }
  .dash-card-body .markdown-container li { margin: 2px 0; }
  .dash-card-body .markdown-container code {
    background: rgba(110,118,129,0.2); padding: 1px 5px; border-radius: 3px; font-size: 0.9em;
  }
  .dash-card-body .markdown-container pre {
    background: var(--bg); padding: 10px; border-radius: 6px; overflow-x: auto; margin: 6px 0;
  }
  .dash-card-body .markdown-container pre code { background: none; padding: 0; }

  /* Empty state */
  .empty-state {
    text-align: center; padding: 60px 24px; color: var(--text-dim); grid-column: 1 / -1;
  }
  .empty-state h2 { font-size: 18px; margin-bottom: 6px; color: var(--text-muted); }
  .empty-state p { font-size: 13px; line-height: 1.6; }
  .empty-state code { background: var(--bg-card); padding: 2px 6px; border-radius: 4px; color: var(--accent); }

  /* Fullscreen overlay */
  .fullscreen-overlay {
    display: none; position: fixed; inset: 0; z-index: 150;
    background: rgba(0,0,0,0.85); backdrop-filter: blur(4px); padding: 40px; overflow: auto;
  }
  .fullscreen-overlay.active { display: flex; align-items: center; justify-content: center; }
  .fullscreen-overlay .fs-content {
    max-width: 95vw; max-height: 95vh; overflow: auto;
    background: var(--bg-card); border-radius: var(--radius); padding: 24px;
  }
  .fullscreen-overlay .close-btn {
    position: fixed; top: 16px; right: 16px;
    background: var(--bg-card); border: 1px solid var(--border);
    color: var(--text); width: 36px; height: 36px; border-radius: 50%;
    cursor: pointer; font-size: 18px; display: flex; align-items: center; justify-content: center;
  }
  .toast {
    position: fixed; bottom: 20px; right: 20px;
    background: var(--bg-card); border: 1px solid var(--green);
    color: var(--green); padding: 8px 16px; border-radius: var(--radius);
    font-size: 13px; opacity: 0; transform: translateY(10px);
    transition: all 0.3s; pointer-events: none; z-index: 200;
  }
  .toast.show { opacity: 1; transform: translateY(0); }
</style>
</head>
<body>
<div id="sidebar">
  <div id="sidebar-header">
    <h1><span class="dot"></span> Claude Viz</h1>
    <button class="clear-btn" onclick="clearAll()">Clear</button>
  </div>
  <div id="session-filter"></div>
  <div id="page-list"></div>
</div>
<div id="main">
  <div id="page-header" style="display:none">
    <div id="page-title"></div>
    <div id="page-meta"></div>
  </div>
  <div id="page-source-files" style="display:none"></div>
  <div id="dashboard">
    <div class="empty-state" id="empty">
      <h2>Waiting for visualizations...</h2>
      <p>Claude will push dashboard pages here as you chat.<br>Ask Claude to <code>/visualize</code> something.</p>
    </div>
  </div>
</div>
<div class="fullscreen-overlay" id="fullscreen" onclick="closeFullscreen(event)">
  <button class="close-btn" onclick="closeFullscreen(event)">&times;</button>
  <div class="fs-content" id="fs-content"></div>
</div>
<div class="toast" id="toast"></div>

<script type="module">
import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs';
mermaid.initialize({ startOnLoad: false, theme: 'dark', securityLevel: 'loose' });

const pageListEl = document.getElementById('page-list');
const sessionFilterEl = document.getElementById('session-filter');
const dashboardEl = document.getElementById('dashboard');
const emptyEl = document.getElementById('empty');
const pageHeaderEl = document.getElementById('page-header');
const pageTitleEl = document.getElementById('page-title');
const pageMetaEl = document.getElementById('page-meta');
const pageSourceEl = document.getElementById('page-source-files');
const fullscreenEl = document.getElementById('fullscreen');
const fsContentEl = document.getElementById('fs-content');
const toastEl = document.getElementById('toast');

const allPages = [];
const seenIds = new Set();
const sessions = new Map();
let activePageId = null;
let activeSessionFilter = null;

const SESSION_COLORS = ['#58a6ff','#3fb950','#bc8cff','#d29922','#f85149','#79c0ff','#56d364','#d2a8ff'];
function sessionColor(id) {
  let h = 0;
  for (let i = 0; i < id.length; i++) h = ((h << 5) - h + id.charCodeAt(i)) | 0;
  return SESSION_COLORS[Math.abs(h) % SESSION_COLORS.length];
}

function connect() {
  const es = new EventSource('/api/events');
  es.onmessage = (e) => {
    const page = JSON.parse(e.data);
    if (seenIds.has(page.id)) return;
    seenIds.add(page.id);
    addPage(page);
  };
}

async function hydrate() {
  try {
    const res = await fetch('/api/pages');
    const pgs = await res.json();
    for (const p of pgs) {
      seenIds.add(p.id);
      addPage(p, true);
    }
  } catch {}
  connect();
}

function addPage(page, silent) {
  if (!sessions.has(page.sessionId)) {
    sessions.set(page.sessionId, { name: page.sessionName, color: sessionColor(page.sessionId) });
  }
  sessions.get(page.sessionId).name = page.sessionName;

  allPages.unshift(page); // newest first
  renderSidebar();
  renderSessionFilter();

  // Auto-select the newest page (unless we're looking at something and this is hydration)
  if (!silent) {
    selectPage(page.id);
  } else if (!activePageId) {
    selectPage(page.id);
  }
}

function renderSidebar() {
  let html = '';
  for (const page of allPages) {
    const hidden = activeSessionFilter && page.sessionId !== activeSessionFilter;
    const active = page.id === activePageId;
    const sess = sessions.get(page.sessionId);
    const time = new Date(page.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    html += '<div class="page-item' + (active ? ' active' : '') + (hidden ? ' hidden-by-filter' : '')
      + '" onclick="selectPage(\\'' + page.id + '\\')" data-id="' + page.id + '">'
      + '<div class="page-item-title">' + escapeHtml(page.title) + '</div>'
      + '<div class="page-item-meta">'
      + '<span class="page-item-session-dot" style="background:' + sess.color + '"></span>'
      + '<span>' + escapeHtml(sess.name) + '</span>'
      + '<span>' + time + '</span>'
      + '<span class="card-count">' + page.cards.length + '</span>'
      + '</div></div>';
  }
  pageListEl.innerHTML = html;
}

function renderSessionFilter() {
  if (sessions.size <= 1) {
    sessionFilterEl.className = '';
    return;
  }
  sessionFilterEl.className = 'visible';
  let html = '<div class="session-pill' + (activeSessionFilter === null ? ' active' : '')
    + '" onclick="filterSession(null)">All</div>';
  for (const [id, sess] of sessions) {
    html += '<div class="session-pill' + (activeSessionFilter === id ? ' active' : '')
      + '" onclick="filterSession(\\'' + id + '\\')">'
      + escapeHtml(sess.name) + '</div>';
  }
  sessionFilterEl.innerHTML = html;
}

window.filterSession = function(sessionId) {
  activeSessionFilter = sessionId;
  renderSidebar();
  renderSessionFilter();
  // If current page is now hidden, select first visible
  if (sessionId) {
    const current = allPages.find(p => p.id === activePageId);
    if (current && current.sessionId !== sessionId) {
      const first = allPages.find(p => p.sessionId === sessionId);
      if (first) selectPage(first.id);
    }
  }
};

window.selectPage = async function(pageId) {
  activePageId = pageId;
  const page = allPages.find(p => p.id === pageId);
  if (!page) return;

  // Update sidebar active state
  document.querySelectorAll('.page-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === pageId);
  });

  // Render header
  const time = new Date(page.timestamp).toLocaleTimeString();
  const sess = sessions.get(page.sessionId);
  pageTitleEl.textContent = page.title;
  pageMetaEl.textContent = sess.name + ' — ' + time;
  pageHeaderEl.style.display = 'flex';

  // Source files
  if (page.sourceFiles && page.sourceFiles.length > 0) {
    pageSourceEl.innerHTML = page.sourceFiles.map(f =>
      '<a href="vscode://file' + escapeHtml(f) + '" onclick="copyPath(event,\\'' + escapeHtml(f) + '\\')">'
      + escapeHtml(f.split('/').pop()) + '</a>'
    ).join('');
    pageSourceEl.style.display = 'flex';
  } else {
    pageSourceEl.style.display = 'none';
  }

  // Render dashboard cards
  emptyEl.style.display = 'none';
  dashboardEl.innerHTML = '';

  for (let i = 0; i < page.cards.length; i++) {
    const card = page.cards[i];
    const cardEl = document.createElement('div');
    const badgeClass = card.type === 'mermaid' ? 'mermaid' : card.type === 'kroki' ? 'kroki' : card.type;
    const badgeLabel = card.type === 'kroki' ? (card.krokiDiagramType || 'kroki') : card.type;
    cardEl.className = 'dash-card' + (card.size === 'full' ? ' full' : '');
    const lightDefault = card.type === 'kroki' || card.type === 'svg';
    cardEl.innerHTML =
      '<div class="dash-card-header">'
      + '<div class="dash-card-header-left">'
      + '<span class="dash-card-badge ' + badgeClass + '">' + badgeLabel + '</span>'
      + (card.title ? '<span class="dash-card-title">' + escapeHtml(card.title) + '</span>' : '')
      + '</div>'
      + '<div class="dash-card-actions">'
      + '<button class="bg-toggle' + (lightDefault ? ' light' : '') + '" onclick="toggleBg(\\'' + pageId + '\\',' + i + ')" title="Toggle light/dark background"></button>'
      + '<button onclick="expandCard(' + i + ')" title="Fullscreen">&#9974;</button>'
      + '<button onclick="copyCard(' + i + ')" title="Copy source">&#128203;</button>'
      + '</div></div>'
      + '<div class="dash-card-body' + (lightDefault ? ' light-bg' : '') + '"><div class="render-target" id="rt-' + pageId + '-' + i + '"></div></div>';
    dashboardEl.appendChild(cardEl);
  }

  // Render card contents
  for (let i = 0; i < page.cards.length; i++) {
    await renderCard(page.cards[i], 'rt-' + pageId + '-' + i);
  }
};

async function renderCard(card, targetId) {
  const target = document.getElementById(targetId);
  if (!target) return;

  if (card.type === 'mermaid') {
    try {
      const { svg } = await mermaid.render('m-' + targetId, card.content);
      target.innerHTML = '<div class="mermaid-container">' + svg + '</div>';
    } catch (err) {
      target.innerHTML = '<pre style="color:var(--red)">' + escapeHtml(err.message) + '</pre><pre>' + escapeHtml(card.content) + '</pre>';
    }
  } else if (card.type === 'kroki') {
    const fmt = card.krokiOutputFormat || 'svg';
    const dtype = card.krokiDiagramType || 'graphviz';
    try {
      const res = await fetch('https://kroki.io/' + dtype + '/' + fmt, {
        method: 'POST', headers: { 'Content-Type': 'text/plain' }, body: card.content
      });
      if (fmt === 'svg') {
        target.innerHTML = '<div class="kroki-container">' + await res.text() + '</div>';
      } else {
        target.innerHTML = '<div class="kroki-container"><img src="' + URL.createObjectURL(await res.blob()) + '" /></div>';
      }
    } catch (err) {
      target.innerHTML = '<pre style="color:var(--red)">Kroki error: ' + escapeHtml(err.message) + '</pre>';
    }
  } else if (card.type === 'html') {
    target.innerHTML = '<div class="html-container">' + card.content + '</div>';
  } else if (card.type === 'svg') {
    target.innerHTML = '<div class="kroki-container">' + card.content + '</div>';
  } else if (card.type === 'markdown') {
    target.innerHTML = '<div class="markdown-container">' + renderMarkdown(card.content) + '</div>';
  }
}

function renderMarkdown(md) {
  // Process blocks: split by double newlines
  const blocks = md.split(/\\n\\n+/);
  return blocks.map(block => {
    // Headings
    if (/^### /.test(block)) return '<h3>' + block.replace(/^### /, '') + '</h3>';
    if (/^## /.test(block)) return '<h2>' + block.replace(/^## /, '') + '</h2>';
    if (/^# /.test(block)) return '<h1>' + block.replace(/^# /, '') + '</h1>';
    // Code blocks
    if (/^\\\`\\\`\\\`/.test(block)) {
      const lines = block.split(/\\n/);
      return '<pre><code>' + escapeHtml(lines.slice(1, -1).join('\\n')) + '</code></pre>';
    }
    // Tables (lines starting with |)
    if (/^\\|/.test(block)) {
      const rows = block.split(/\\n/).filter(r => r.trim());
      if (rows.length < 2) return '<p>' + inlineFormat(block) + '</p>';
      const isSep = function(r) { return /^\\|?[\\s\\-:]+([\\|][\\s\\-:]+)*\\|?$/.test(r.trim()); };
      const sepIdx = rows.findIndex((r, i) => i > 0 && isSep(r));
      const hasHeader = sepIdx === 1;
      const parseCells = function(row) {
        return row.replace(/^\\|/, '').replace(/\\|$/, '').split('\\|').map(c => c.trim());
      };
      let html = '<table style="width:100%;border-collapse:collapse;font-size:13px;margin:4px 0;">';
      if (hasHeader) {
        const hCells = parseCells(rows[0]);
        html += '<thead><tr>' + hCells.map(c =>
          '<th style="padding:6px 10px;border-bottom:2px solid var(--border);text-align:left;font-weight:600;color:var(--text);">'
          + inlineFormat(escapeHtml(c)) + '</th>'
        ).join('') + '</tr></thead>';
      }
      html += '<tbody>';
      const startIdx = hasHeader ? 2 : 0;
      for (let ri = startIdx; ri < rows.length; ri++) {
        if (isSep(rows[ri])) continue;
        const cells = parseCells(rows[ri]);
        html += '<tr>' + cells.map(c =>
          '<td style="padding:5px 10px;border-bottom:1px solid var(--border);color:var(--text-muted);">'
          + inlineFormat(escapeHtml(c)) + '</td>'
        ).join('') + '</tr>';
      }
      html += '</tbody></table>';
      return html;
    }
    // Lists
    if (/^- /.test(block)) {
      const items = block.split(/\\n/).filter(l => l.startsWith('- '));
      return '<ul>' + items.map(l => '<li>' + inlineFormat(l.replace(/^- /, '')) + '</li>').join('') + '</ul>';
    }
    // Paragraph
    return '<p>' + inlineFormat(block.replace(/\\n/g, ' ')) + '</p>';
  }).join('');
}

function inlineFormat(s) {
  return s
    .replace(/\\\`([^\\\`]+)\\\`/g, '<code>$1</code>')
    .replace(/\\*\\*(.+?)\\*\\*/g, '<strong>$1</strong>')
    .replace(/\\*(.+?)\\*/g, '<em>$1</em>');
}

function escapeHtml(s) {
  const d = document.createElement('div');
  d.textContent = s || '';
  return d.innerHTML;
}

window.toggleBg = function(pageId, cardIdx) {
  const body = document.getElementById('rt-' + pageId + '-' + cardIdx)?.parentElement;
  if (!body) return;
  const isLight = body.classList.toggle('light-bg');
  const card = body.parentElement;
  const btn = card.querySelector('.bg-toggle');
  if (btn) btn.classList.toggle('light', isLight);
};

window.expandCard = function(cardIdx) {
  const page = allPages.find(p => p.id === activePageId);
  if (!page) return;
  const targetId = 'rt-' + activePageId + '-' + cardIdx;
  const target = document.getElementById(targetId);
  if (target) {
    const isLight = target.parentElement.classList.contains('light-bg');
    fsContentEl.innerHTML = target.innerHTML;
    fsContentEl.style.background = isLight ? '#f6f8fa' : '';
    fullscreenEl.classList.add('active');
  }
};

window.copyCard = function(cardIdx) {
  const page = allPages.find(p => p.id === activePageId);
  if (!page || !page.cards[cardIdx]) return;
  navigator.clipboard.writeText(page.cards[cardIdx].content).then(() => showToast('Source copied to clipboard'));
};

window.copyPath = function(e, path) {
  e.preventDefault();
  navigator.clipboard.writeText(path).then(() => showToast('Path copied: ' + path));
  window.open(e.target.href, '_blank');
};

window.closeFullscreen = function(e) {
  if (e.target === fullscreenEl || e.target.classList.contains('close-btn')) {
    fullscreenEl.classList.remove('active');
  }
};

window.clearAll = async function() {
  const url = activeSessionFilter ? '/api/pages?session_id=' + encodeURIComponent(activeSessionFilter) : '/api/pages';
  await fetch(url, { method: 'DELETE' });
  if (activeSessionFilter) {
    for (let i = allPages.length - 1; i >= 0; i--) {
      if (allPages[i].sessionId === activeSessionFilter) {
        seenIds.delete(allPages[i].id);
        allPages.splice(i, 1);
      }
    }
    sessions.delete(activeSessionFilter);
    activeSessionFilter = null;
  } else {
    allPages.length = 0;
    seenIds.clear();
    sessions.clear();
  }
  activePageId = null;
  dashboardEl.innerHTML = '<div class="empty-state" id="empty"><h2>Waiting for visualizations...</h2><p>Claude will push dashboard pages here as you chat.</p></div>';
  pageHeaderEl.style.display = 'none';
  pageSourceEl.style.display = 'none';
  renderSidebar();
  renderSessionFilter();
  // Select first available page
  if (allPages.length > 0) selectPage(allPages[0].id);
};

function showToast(msg) {
  toastEl.textContent = msg;
  toastEl.classList.add('show');
  setTimeout(() => toastEl.classList.remove('show'), 2000);
}

document.addEventListener('keydown', (e) => {
  if (e.key === 'Escape') fullscreenEl.classList.remove('active');
  if (e.key === 'ArrowUp' || e.key === 'ArrowDown') {
    const visible = allPages.filter(p => !activeSessionFilter || p.sessionId === activeSessionFilter);
    const idx = visible.findIndex(p => p.id === activePageId);
    const next = e.key === 'ArrowUp' ? Math.max(0, idx - 1) : Math.min(visible.length - 1, idx + 1);
    if (visible[next]) selectPage(visible[next].id);
  }
});

hydrate();
</script>
</body>
</html>`;

const server = Bun.serve({
  hostname: HOST,
  port: PORT,
  fetch(req) {
    const url = new URL(req.url);

    if (url.pathname === "/" || url.pathname === "/index.html") {
      return new Response(HTML_PAGE, { headers: { "Content-Type": "text/html; charset=utf-8" } });
    }

    // SSE
    if (url.pathname === "/api/events") {
      let ctrl: ReadableStreamDefaultController;
      const stream = new ReadableStream({
        start(c) { ctrl = c; sseClients.add(c); },
        cancel() { sseClients.delete(ctrl); },
      });
      return new Response(stream, {
        headers: { "Content-Type": "text/event-stream", "Cache-Control": "no-cache", Connection: "keep-alive", "Access-Control-Allow-Origin": "*" },
      });
    }

    // GET pages
    if (url.pathname === "/api/pages" && req.method === "GET") {
      const sid = url.searchParams.get("session_id");
      return Response.json(sid ? pages.filter(p => p.sessionId === sid) : pages);
    }

    // POST page (new dashboard)
    if (url.pathname === "/api/pages" && req.method === "POST") {
      return (async () => {
        let body: any;
        try { body = await req.json(); } catch {
          return Response.json({ ok: false, error: "Invalid JSON" }, { status: 400 });
        }

        const sessionId = body.session_id || "default";
        const sessionName = body.session_name || "Default";
        sessionNames.set(sessionId, sessionName);

        // Support both: {cards: [...]} and legacy single-card {type, content, ...}
        let cards: Card[];
        if (Array.isArray(body.cards)) {
          cards = body.cards.map((c: any) => ({
            type: c.type || "mermaid",
            title: c.title || "",
            content: c.content || "",
            krokiDiagramType: c.kroki_diagram_type,
            krokiOutputFormat: c.kroki_output_format || "svg",
            size: c.size || "full",
          }));
        } else {
          // Legacy single-card format
          cards = [{
            type: body.type || "mermaid",
            title: "",
            content: body.content || "",
            krokiDiagramType: body.kroki_diagram_type,
            krokiOutputFormat: body.kroki_output_format || "svg",
            size: "full",
          }];
        }

        const page: Page = {
          id: generateId(),
          title: body.title || "Untitled",
          cards,
          sourceFiles: body.source_files || [],
          sessionId,
          sessionName,
          timestamp: Date.now(),
        };

        pages.push(page);
        broadcast("message", page);
        return Response.json({ ok: true, id: page.id, session_id: sessionId });
      })();
    }

    // DELETE pages
    if (url.pathname === "/api/pages" && req.method === "DELETE") {
      const sid = url.searchParams.get("session_id");
      if (sid) {
        for (let i = pages.length - 1; i >= 0; i--) {
          if (pages[i].sessionId === sid) pages.splice(i, 1);
        }
        sessionNames.delete(sid);
      } else {
        pages.length = 0;
        sessionNames.clear();
      }
      return Response.json({ ok: true });
    }

    // Legacy: POST /api/visualizations -> redirect to pages
    if (url.pathname === "/api/visualizations" && req.method === "POST") {
      // Rewrite to /api/pages
      return server.fetch(new Request(url.origin + "/api/pages", {
        method: "POST",
        headers: req.headers,
        body: req.body,
      }));
    }

    // Health
    if (url.pathname === "/api/health") {
      return Response.json({ status: "ok", pages: pages.length, sessions: sessionNames.size });
    }

    // CORS
    if (req.method === "OPTIONS") {
      return new Response(null, {
        headers: { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "GET, POST, DELETE, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" },
      });
    }

    return new Response("Not Found", { status: 404 });
  },
});

console.log(`Claude Viz server running at http://${HOST}:${PORT}`);
