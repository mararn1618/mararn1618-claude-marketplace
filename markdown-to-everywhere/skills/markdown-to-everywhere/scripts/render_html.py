#!/usr/bin/env python3
"""Convert markdown documents to self-contained HTML with interactive draw.io diagrams.

Features:
  - Status badges: [NEW], [EXISTING], [CHANGED] rendered as colored tags
  - Two-column layouts: <!-- columns --> / <!-- col --> / <!-- /columns -->
  - Draw.io diagrams: ![caption](path.drawio) embedded via JS viewer
  - Graphviz/PlantUML: fenced blocks rendered via Kroki.io
  - Auto-discovers NN-*.md files, generates nav bar and index page
  - Zero external Python dependencies (stdlib only)

Usage:
  python3 render_html.py /path/to/doc-directory
  cd /path/to/doc-directory/html && python3 -m http.server 8765

The HTML directory must be served over HTTP (not file://) because the draw.io
viewer fetches .drawio files via XHR.
"""

import re
import zlib
import base64
import sys
import html as html_mod
import urllib.parse
import shutil
from pathlib import Path


# ============================================================
# Diagram helpers
# ============================================================

def kroki_encode(source, diagram_type="graphviz"):
    compressed = zlib.compress(source.encode('utf-8'), 9)
    encoded = base64.urlsafe_b64encode(compressed).decode('ascii')
    return f'https://kroki.io/{diagram_type}/svg/{encoded}'


def diagram_to_img(source, diagram_type="graphviz"):
    url = kroki_encode(source.strip(), diagram_type)
    return f'<img src="{url}" alt="diagram" class="diagram" />'


def drawio_to_embed(drawio_path, base_dir):
    """Embed a .drawio file via the draw.io JS viewer using URL reference.

    CRITICAL: Never inline draw.io XML in HTML attributes. XML entities,
    single quotes in <?xml>, and double-encoding chains break JSON.parse.
    URL-based loading avoids all of this.
    """
    full_path = base_dir / drawio_path
    if not full_path.exists():
        return f'<p class="error">Diagram not found: {drawio_path}</p>'
    html_dir = base_dir / 'html'
    dest = html_dir / Path(drawio_path).name
    shutil.copy2(full_path, dest)
    filename = Path(drawio_path).name
    return (
        f'<div class="drawio-diagram">'
        f'<div class="mxgraph" style="max-width:100%;border:1px solid #e2e8f0;'
        f'border-radius:6px;background:white;" '
        f"""data-mxgraph='{{"highlight":"#0000ff","nav":true,"resize":true,"""
        f""""toolbar":"zoom layers lightbox","url":"{filename}"}}'></div></div>"""
    )


# ============================================================
# Markdown to HTML converter
# ============================================================

def md_to_html(md_text, base_dir):
    lines = md_text.split('\n')
    out = []
    in_diagram = False
    in_code = False
    in_table = False
    diagram_type = None
    diagram_buf = []
    table_buf = []
    list_stack = []  # stack of ('ul'|'ol', indent_level)
    i = 0

    while i < len(lines):
        line = lines[i]

        # Multi-column layout
        if line.strip() == '<!-- columns -->':
            out.append('<div class="columns"><div class="col">')
            i += 1; continue
        if line.strip() == '<!-- /columns -->':
            while list_stack:
                closing_tag = list_stack.pop()[0]
                out.append(f'</li></{closing_tag}>')
            out.append('</div></div>')
            i += 1; continue
        if line.strip() == '<!-- col -->':
            while list_stack:
                closing_tag = list_stack.pop()[0]
                out.append(f'</li></{closing_tag}>')
            out.append('</div><div class="col">')
            i += 1; continue

        # Diagram fenced blocks (graphviz, plantuml, dot)
        m_diagram = re.match(r'^```(graphviz|plantuml|dot)\s*$', line)
        if m_diagram and not in_code:
            in_diagram = True
            dtype = m_diagram.group(1)
            diagram_type = "plantuml" if dtype == "plantuml" else "graphviz"
            diagram_buf = []
            i += 1; continue
        if in_diagram and line.strip() == '```':
            in_diagram = False
            out.append(diagram_to_img('\n'.join(diagram_buf), diagram_type))
            i += 1; continue
        if in_diagram:
            diagram_buf.append(line)
            i += 1; continue

        # Draw.io image references
        m_drawio = re.match(r'^!\[([^\]]*)\]\(([^)]+\.drawio)\)\s*$', line)
        if m_drawio:
            caption = m_drawio.group(1)
            drawio_path = m_drawio.group(2)
            out.append(drawio_to_embed(drawio_path, base_dir))
            if caption:
                out.append(f'<p class="diagram-caption"><em>{html_mod.escape(caption)}</em></p>')
            i += 1; continue

        # Code blocks
        if re.match(r'^```', line) and not in_code:
            lang = line.strip('`').strip()
            in_code = True
            out.append(f'<pre><code class="{html_mod.escape(lang)}">')
            i += 1; continue
        if in_code and line.strip() == '```':
            in_code = False
            out.append('</code></pre>')
            i += 1; continue
        if in_code:
            out.append(html_mod.escape(line))
            i += 1; continue

        # Tables
        if '|' in line and line.strip().startswith('|'):
            if not in_table:
                in_table = True
                table_buf = []
            table_buf.append(line)
            i += 1; continue
        elif in_table:
            in_table = False
            out.append(render_table(table_buf))
            table_buf = []

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = inline_format(m.group(2))
            anchor = re.sub(r'[^a-z0-9-]', '', re.sub(r'\s+', '-', m.group(2).lower().strip()))
            out.append(f'<h{level} id="{anchor}">{text}</h{level}>')
            i += 1; continue

        # Horizontal rule
        if re.match(r'^---+\s*$', line):
            out.append('<hr/>')
            i += 1; continue

        # Blockquotes
        if line.startswith('>'):
            text = inline_format(line.lstrip('> '))
            out.append(f'<blockquote><p>{text}</p></blockquote>')
            i += 1; continue

        # List items (unordered and ordered, with nesting)
        m_ul = re.match(r'^(\s*)[-*]\s+(.*)', line)
        m_ol = re.match(r'^(\s*)\d+\.\s+(.*)', line)
        if m_ul or m_ol:
            m = m_ul or m_ol
            indent = len(m.group(1))
            text = inline_format(m.group(2))
            tag = 'ul' if m_ul else 'ol'

            if not list_stack:
                out.append(f'<{tag}>')
                list_stack.append((tag, indent))
            else:
                _, prev_indent = list_stack[-1]
                if indent > prev_indent:
                    out.append(f'<{tag}>')
                    list_stack.append((tag, indent))
                else:
                    while len(list_stack) > 1 and list_stack[-1][1] > indent:
                        closing_tag = list_stack.pop()[0]
                        out.append(f'</li></{closing_tag}>')
                    if list_stack and list_stack[-1][0] != tag:
                        closing_tag = list_stack.pop()[0]
                        out.append(f'</{closing_tag}>')
                        out.append(f'<{tag}>')
                        list_stack.append((tag, indent))
                    else:
                        out.append('</li>')

            out.append(f'<li>{text}')
            i += 1; continue

        # Empty line: check if a list continues after the gap
        if line.strip() == '':
            if list_stack:
                # Look ahead: if next non-blank line is a list item, keep list open
                j = i + 1
                while j < len(lines) and lines[j].strip() == '':
                    j += 1
                if j < len(lines) and (re.match(r'^(\s*)[-*]\s+', lines[j]) or re.match(r'^(\s*)\d+\.\s+', lines[j])):
                    i += 1; continue  # skip blank line, keep list open
            # Close any open lists when we hit a blank non-continuation line
            if list_stack:
                while list_stack:
                    closing_tag = list_stack.pop()[0]
                    out.append(f'</li></{closing_tag}>')
            out.append('')
            i += 1; continue

        # Close any open lists when we hit a non-list line
        if list_stack:
            while list_stack:
                closing_tag = list_stack.pop()[0]
                out.append(f'</li></{closing_tag}>')

        # HTML comments (skip)
        if line.strip().startswith('<!--'):
            i += 1; continue

        # Paragraph
        out.append(f'<p>{inline_format(line)}</p>')
        i += 1

    if in_table:
        out.append(render_table(table_buf))

    return '\n'.join(out)


def render_table(rows):
    if len(rows) < 2:
        return ''
    h = ['<table>']
    cells = [c.strip() for c in rows[0].strip('|').split('|')]
    h.append('<thead><tr>')
    for cell in cells:
        h.append(f'<th>{inline_format(cell.strip())}</th>')
    h.append('</tr></thead><tbody>')
    for row in rows[2:]:
        cells = [c.strip() for c in row.strip('|').split('|')]
        h.append('<tr>')
        for cell in cells:
            h.append(f'<td>{inline_format(cell.strip())}</td>')
        h.append('</tr>')
    h.append('</tbody></table>')
    return '\n'.join(h)


def inline_format(text):
    text = html_mod.escape(text)
    # Code spans first (protect their content from bold/italic processing)
    text = re.sub(r'`(.+?)`', r'<code>\1</code>', text)
    # Bold (must come before italic)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    # Italic: require non-space after opening * and before closing *
    text = re.sub(r'\*(\S.*?\S)\*', r'<em>\1</em>', text)
    text = re.sub(r'\*(\S)\*', r'<em>\1</em>', text)  # single char italic
    def _md_link(m):
        label, href = m.group(1), m.group(2)
        if href.endswith('.md'):
            href = href[:-3] + '.html'
        return f'<a href="{href}">{label}</a>'
    text = re.sub(r'\[(.+?)\]\((.+?)\)', _md_link, text)
    # Status badges (longest patterns first to avoid partial matches)
    tag_replacements = [
        ('[EXISTING, extended]', 'changed'), ('[EXISTING - reframed]', 'changed'),
        ('[NEW - GREENFIELD]', 'new'), ('[NEW: GREENFIELD]', 'new'),
        ('[CHANGED - mostly GREENFIELD]', 'changed'),
        ('[NEW/BLOCKED]', 'new'), ('[EXISTING/CHANGED]', 'changed'),
        ('[EXISTING]', 'existing'), ('[CHANGED]', 'changed'),
        ('[REVISED]', 'changed'), ('[NEW]', 'new'), ('[GREENFIELD]', 'new'),
    ]
    for tag_text, css_class in tag_replacements:
        text = text.replace(
            html_mod.escape(tag_text),
            f'<span class="tag {css_class}">{html_mod.escape(tag_text)}</span>'
        )
    return text


# ============================================================
# CSS Design System
# ============================================================

CSS = """
:root {
    --bg: #ffffff; --fg: #1a1a2e; --accent: #2563eb;
    --border: #e2e8f0; --code-bg: #f1f5f9; --table-stripe: #f8fafc;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--fg); background: var(--bg); max-width: 1060px; margin: 0 auto;
  padding: 2rem 1.5rem; line-height: 1.65; font-size: 15px; }
h1 { font-size: 1.8rem; margin: 2rem 0 1rem; border-bottom: 2px solid var(--accent); padding-bottom: 0.3rem; }
h2 { font-size: 1.4rem; margin: 1.8rem 0 0.8rem; color: var(--accent); }
h3 { font-size: 1.15rem; margin: 1.4rem 0 0.6rem; }
p { margin: 0.5rem 0; }
hr { border: none; border-top: 1px solid var(--border); margin: 1.5rem 0; }
code { background: var(--code-bg); padding: 0.15rem 0.4rem; border-radius: 3px; font-size: 0.9em; }
pre { background: var(--code-bg); padding: 1rem; border-radius: 6px; overflow-x: auto; margin: 0.8rem 0; }
pre code { background: none; padding: 0; font-size: 0.85em; }
table { width: 100%; border-collapse: collapse; margin: 0.8rem 0; font-size: 0.92em; }
th { background: var(--code-bg); text-align: left; padding: 0.5rem 0.7rem; border: 1px solid var(--border); font-weight: 600; }
td { padding: 0.45rem 0.7rem; border: 1px solid var(--border); vertical-align: top; }
tbody tr:nth-child(even) { background: var(--table-stripe); }
blockquote { border-left: 3px solid var(--accent); padding: 0.5rem 1rem; margin: 0.8rem 0; background: #eff6ff; border-radius: 0 4px 4px 0; }
li { margin: 0.25rem 0; margin-left: 1.5rem; }
a { color: var(--accent); text-decoration: none; }
a:hover { text-decoration: underline; }
.tag { font-weight: 700; font-size: 0.82em; padding: 0.1rem 0.4rem; border-radius: 3px; white-space: nowrap; }
.tag.existing { color: #059669; background: #ecfdf5; }
.tag.new { color: #2563eb; background: #eff6ff; }
.tag.changed { color: #d97706; background: #fffbeb; }
.diagram { max-width: 100%; margin: 1rem auto; display: block; }
.drawio-diagram { margin: 1rem 0; }
.drawio-diagram svg { max-width: 100%; height: auto; }
.columns { display: flex; gap: 1.5rem; align-items: flex-start; margin: 1rem 0; }
.columns > .col { flex: 1; min-width: 0; }
.columns > .drawio-diagram { flex: 0 0 55%; max-width: 55%; }
.columns > .drawio-diagram + .col { flex: 0 0 42%; }
@media (max-width: 768px) { .columns { flex-direction: column; } .columns > .drawio-diagram { max-width: 100%; } }
.diagram-caption { text-align: center; color: #666; font-size: 0.9em; margin-top: 0.3rem; }
.error { color: #cc0000; background: #fff0f0; padding: 0.5rem; border-radius: 4px; }
nav.doc-nav { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; padding: 0.8rem; background: var(--code-bg); border-radius: 6px; }
nav.doc-nav a { padding: 0.3rem 0.8rem; border-radius: 4px; font-weight: 500; font-size: 0.9em; }
nav.doc-nav a.active { background: var(--accent); color: white; }
"""

DRAWIO_VIEWER = '<script type="text/javascript" src="https://viewer.diagrams.net/js/viewer-static.min.js"></script>'


# ============================================================
# Page assembly
# ============================================================

def build_nav(nav_items, current_file):
    links = []
    for href, label in nav_items:
        cls = ' class="active"' if href == current_file else ''
        links.append(f'<a href="{href}"{cls}>{label}</a>')
    return '<nav class="doc-nav">' + ''.join(links) + '</nav>'


def build_html(title, body, nav_items, current_file, has_drawio=False):
    viewer = DRAWIO_VIEWER if has_drawio else ""
    nav = build_nav(nav_items, current_file)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{html_mod.escape(title)}</title>
<style>{CSS}</style>
</head>
<body>
{nav}
{body}
{viewer}
</body>
</html>"""


# ============================================================
# Main: auto-discover and render
# ============================================================

def main():
    base = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('.')
    html_dir = base / 'html'
    html_dir.mkdir(exist_ok=True)

    # Auto-discover markdown files matching NN-*.md pattern
    md_files = sorted(base.glob('[0-9][0-9]-*.md'))
    if not md_files:
        print("No NN-*.md files found. Looking for any .md files...")
        md_files = sorted(f for f in base.glob('*.md')
                          if f.name not in ('README.md', 'CLAUDE.md', 'MEMORY.md'))

    if not md_files:
        print("No markdown files found.")
        sys.exit(1)

    # Build nav items from discovered files
    nav_items = []
    for md_path in md_files:
        html_name = md_path.stem + '.html'
        # Derive short label from filename
        label = md_path.stem
        if re.match(r'^\d+-', label):
            label = label.split('-', 1)[1]
        label = label.replace('-', ' ').title()
        nav_items.append((html_name, label))

    # Convert each file
    for md_path in md_files:
        print(f"Converting {md_path.name}...")
        md_text = md_path.read_text(encoding='utf-8')
        # Derive title from H1 or filename
        m = re.match(r'^#\s+(.+)', md_text)
        title = m.group(1) if m else md_path.stem.replace('-', ' ').title()
        body = md_to_html(md_text, base)
        has_drawio = '.drawio' in md_text or 'mxgraph' in body
        html_name = md_path.stem + '.html'
        html_content = build_html(title, body, nav_items, html_name, has_drawio)
        (html_dir / html_name).write_text(html_content, encoding='utf-8')
        print(f"  -> html/{html_name}")

    # Index page
    index_body = "<h1>Documentation</h1><ul>"
    for href, label in nav_items:
        index_body += f'<li><a href="{href}">{label}</a></li>'
    index_body += "</ul>"
    index_html = build_html("Documentation", index_body, nav_items, "", False)
    (html_dir / "index.html").write_text(index_html, encoding='utf-8')
    print("  -> html/index.html")
    print("Done! Serve with: cd html && python3 -m http.server 8765")


if __name__ == '__main__':
    main()
