#!/usr/bin/env python3
"""Publish markdown documents to Confluence Cloud with draw.io diagrams.

Converts markdown (with status badges, two-column layouts, code blocks, tables)
to Confluence storage format. Uploads .drawio files as page attachments and
embeds them via the draw.io Confluence macro.

Usage:
  python3 publish_confluence.py --config confluence.json

Config file format (confluence.json):
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
      "diagrams": ["03-outbound-pipeline.drawio", "04-inbound-pipeline.drawio"]
    }
  ]
}

Authentication:
  The session_token is a JWT from the tenant.session.token cookie in your browser.
  To get it: open Confluence in browser, log in, then:
    - Browser DevTools > Application > Cookies > tenant.session.token
    - OR via playwright-cli: playwright-cli cookie-get tenant.session.token

Zero external Python dependencies (stdlib only).
"""

import json
import os
import re
import sys
import urllib.request
import urllib.error
import subprocess
from pathlib import Path


# ============================================================
# Confluence API helpers
# ============================================================

def upload_attachment(base_url, session_token, page_id, filepath):
    """Upload or update a file attachment on a Confluence page.

    Uses PUT to handle both new and existing attachments (POST fails if
    an attachment with the same filename already exists).

    Returns (content_id, page_id, version) on success, None on failure.
    The version is needed for the draw.io macro's contentVer/revision params.
    """
    result = subprocess.run([
        "curl", "-s", "-X", "PUT",
        f"{base_url}/rest/api/content/{page_id}/child/attachment",
        "-H", "X-Atlassian-Token: no-check",
        "-H", f"Cookie: tenant.session.token={session_token}",
        "-F", f"file=@{filepath};type=application/xml",
        "-F", "minorEdit=true"
    ], capture_output=True, text=True)
    try:
        d = json.loads(result.stdout)
        results = d.get('results', [])
        if results:
            att_id = results[0]['id'].replace('att', '')
            att_ver = results[0].get('version', {}).get('number', 1)
            return (att_id, page_id, att_ver)
    except (json.JSONDecodeError, KeyError, IndexError):
        pass
    print(f"  FAILED to upload {filepath}: {result.stdout[:200]}")
    return None


def get_page_version(base_url, session_token, page_id):
    """Get the current version number of a Confluence page."""
    req = urllib.request.Request(
        f"{base_url}/api/v2/pages/{page_id}",
        headers={"Accept": "application/json",
                 "Cookie": f"tenant.session.token={session_token}"}
    )
    with urllib.request.urlopen(req) as resp:
        d = json.loads(resp.read())
        return d['version']['number']


def update_page(base_url, session_token, page_id, title, content, version):
    """Update a Confluence page with new storage format content."""
    payload = {
        "id": page_id,
        "type": "page",
        "title": title,
        "version": {"number": version},
        "body": {"storage": {"value": content, "representation": "storage"}}
    }
    data = json.dumps(payload).encode('utf-8')
    req = urllib.request.Request(
        f"{base_url}/rest/api/content/{page_id}",
        data=data, method="PUT"
    )
    req.add_header("Content-Type", "application/json")
    req.add_header("Cookie", f"tenant.session.token={session_token}")
    req.add_header("X-Atlassian-Token", "no-check")
    try:
        with urllib.request.urlopen(req) as resp:
            result = json.loads(resp.read())
            print(f"  OK v{result['version']['number']}: {title}")
            return True
    except urllib.error.HTTPError as e:
        print(f"  ERROR {e.code}: {e.read().decode()[:300]}")
        return False


# ============================================================
# Confluence storage format helpers
# ============================================================

def badge(title, colour):
    return (f'<ac:structured-macro ac:name="status" ac:schema-version="1">'
            f'<ac:parameter ac:name="title">{title}</ac:parameter>'
            f'<ac:parameter ac:name="colour">{colour}</ac:parameter>'
            f'</ac:structured-macro>')

BADGES = {
    '[NEW: GREENFIELD]': badge('NEW','Blue') + ' ' + badge('GREENFIELD','Red'),
    '[EXISTING/CHANGED]': badge('EXISTING','Green') + ' ' + badge('CHANGED','Yellow'),
    '[NEW]': badge('NEW','Blue'),
    '[EXISTING]': badge('EXISTING','Green'),
    '[CHANGED]': badge('CHANGED','Yellow'),
    '[GREENFIELD]': badge('GREENFIELD','Red'),
    '[REVISED]': badge('REVISED','Yellow'),
}

def sub_badges(text):
    for k, v in BADGES.items():
        text = text.replace(k, v + ' ')
    return text

def esc(text):
    return text.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')

def inline(text):
    text = sub_badges(text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', text)
    def code_repl(m):
        return '<code>' + esc(m.group(1)) + '</code>'
    text = re.sub(r'`([^`]+)`', code_repl, text)
    return text

def drawio_macro(content_id, page_id, filename, version=1, width=900, height=340):
    """Generate draw.io Confluence macro referencing an uploaded attachment.

    CRITICAL: contentVer and revision must match the actual attachment version.
    If the attachment is updated (new version uploaded), the macro must be
    updated too, otherwise Confluence displays the old cached version.
    """
    return (f'<ac:structured-macro ac:name="drawio" ac:schema-version="1" data-layout="default">'
            f'<ac:parameter ac:name="mVer">2</ac:parameter>'
            f'<ac:parameter ac:name="zoom">1</ac:parameter>'
            f'<ac:parameter ac:name="simple">0</ac:parameter>'
            f'<ac:parameter ac:name="inComment">0</ac:parameter>'
            f'<ac:parameter ac:name="custContentId">{content_id}</ac:parameter>'
            f'<ac:parameter ac:name="pageId">{page_id}</ac:parameter>'
            f'<ac:parameter ac:name="lbox">1</ac:parameter>'
            f'<ac:parameter ac:name="diagramDisplayName">{filename}</ac:parameter>'
            f'<ac:parameter ac:name="contentVer">{version}</ac:parameter>'
            f'<ac:parameter ac:name="revision">{version}</ac:parameter>'
            f'<ac:parameter ac:name="baseUrl">{{}}</ac:parameter>'
            f'<ac:parameter ac:name="diagramName">{filename}</ac:parameter>'
            f'<ac:parameter ac:name="pCenter">0</ac:parameter>'
            f'<ac:parameter ac:name="width">{width}</ac:parameter>'
            f'<ac:parameter ac:name="links" />'
            f'<ac:parameter ac:name="tbstyle" />'
            f'<ac:parameter ac:name="height">{height}</ac:parameter>'
            f'</ac:structured-macro>')

def code_block_macro(code, lang=''):
    lang_param = f'<ac:parameter ac:name="language">{lang}</ac:parameter>' if lang else ''
    escaped = code.replace(']]>', ']]]]><![CDATA[>')
    return (f'<ac:structured-macro ac:name="code" ac:schema-version="1">{lang_param}'
            f'<ac:plain-text-body><![CDATA[{escaped}]]></ac:plain-text-body>'
            f'</ac:structured-macro>')

def note_macro(text):
    return (f'<ac:structured-macro ac:name="note" ac:schema-version="1">'
            f'<ac:rich-text-body><p>{inline(text.strip())}</p></ac:rich-text-body>'
            f'</ac:structured-macro>')


# ============================================================
# Markdown to Confluence storage format converter
# ============================================================

def convert_md(md_text, diagram_map):
    """Convert markdown to Confluence storage format.

    diagram_map: dict mapping 'filename.drawio' to drawio_macro() output string
    """
    lines = md_text.split('\n')
    html = []
    i = 0
    two_col_active = False
    two_col_left = []
    two_col_right = []
    two_col_side = 'left'

    def flush_two_col():
        nonlocal two_col_active, two_col_left, two_col_right, two_col_side
        left = ''.join(two_col_left)
        right = ''.join(two_col_right)
        result = (f'<ac:layout><ac:layout-section ac:type="two_equal" ac:breakout-mode="default">'
                  f'<ac:layout-cell>{left}</ac:layout-cell>'
                  f'<ac:layout-cell>{right}</ac:layout-cell>'
                  f'</ac:layout-section></ac:layout>')
        two_col_active = False
        two_col_left = []
        two_col_right = []
        two_col_side = 'left'
        return result

    def add(s):
        if two_col_active:
            (two_col_left if two_col_side == 'left' else two_col_right).append(s)
        else:
            html.append(s)

    while i < len(lines):
        line = lines[i]

        # Two-column markers
        if line.strip() == '<!-- columns -->':
            two_col_active = True; two_col_side = 'left'; i += 1; continue
        if line.strip() == '<!-- col -->':
            two_col_side = 'right'; i += 1; continue
        if line.strip() == '<!-- /columns -->':
            html.append(flush_two_col()); i += 1; continue

        # Skip nav footer
        if re.match(r'^\[.+\]\(.+\.md\)\s*\|', line):
            i += 1; continue

        # Skip H1 (page title set via API)
        if line.startswith('# ') and not line.startswith('## '):
            i += 1; continue

        # Headings
        for lvl, prefix in [(2, '## '), (3, '### '), (4, '#### ')]:
            if line.startswith(prefix):
                add(f'<h{lvl}>{inline(line[len(prefix):].strip())}</h{lvl}>')
                i += 1; break
        else:
            pass  # fall through
        if any(line.startswith(p) for p in ('## ', '### ', '#### ')):
            continue

        # Horizontal rule
        if line.strip() in ('---', '***', '___'):
            add('<hr/>'); i += 1; continue

        # Blockquote
        if line.startswith('> '):
            bq = [line[2:].strip()]
            while i+1 < len(lines) and lines[i+1].startswith('> '):
                i += 1; bq.append(lines[i][2:].strip())
            add(note_macro(' '.join(bq))); i += 1; continue

        # Fenced code block
        if line.startswith('```'):
            lang = line[3:].strip(); i += 1
            code_lines = []
            while i < len(lines) and not lines[i].startswith('```'):
                code_lines.append(lines[i]); i += 1
            add(code_block_macro('\n'.join(code_lines), lang=lang))
            i += 1; continue

        # Diagram reference
        m = re.match(r'!\[.*?\]\((diagrams/[\w.-]+\.drawio)\)', line)
        if m:
            fname = os.path.basename(m.group(1))
            add(diagram_map.get(fname, f'<p><em>[Diagram: {fname}]</em></p>'))
            i += 1; continue

        # Table
        if line.startswith('|') and i+1 < len(lines) and re.match(r'\|[\s|:-]+\|', lines[i+1]):
            rows_html = '<table><tbody>'
            is_header = True; header_done = False
            while i < len(lines) and lines[i].startswith('|'):
                if re.match(r'\|[\s|:-]+\|', lines[i]):
                    is_header = False; header_done = True; i += 1; continue
                cells = [c.strip() for c in lines[i].strip('|').split('|')]
                tag = 'th' if (is_header and not header_done) else 'td'
                rows_html += '<tr>' + ''.join(f'<{tag}><p>{inline(c)}</p></{tag}>' for c in cells) + '</tr>'
                is_header = False; i += 1
            rows_html += '</tbody></table>'
            add(rows_html); continue

        # Ordered list
        if re.match(r'^\d+\.\s', line):
            items = '<ol>'
            while i < len(lines) and re.match(r'^\d+\.\s', lines[i]):
                m = re.match(r'^\d+\.\s+(.*)', lines[i])
                if m: items += f'<li><p>{inline(m.group(1))}</p></li>'
                i += 1
            items += '</ol>'; add(items); continue

        # Unordered list
        if re.match(r'^[-*+]\s', line):
            items = '<ul>'
            while i < len(lines) and re.match(r'^(\s*)[-*+]\s', lines[i]):
                m = re.match(r'^(\s*)[-*+]\s+(.*)', lines[i])
                if m: items += f'<li><p>{inline(m.group(2))}</p></li>'
                i += 1
            items += '</ul>'; add(items); continue

        # Blank line
        if not line.strip():
            i += 1; continue

        # Paragraph
        add(f'<p>{inline(line)}</p>'); i += 1

    if two_col_active:
        html.append(flush_two_col())
    return '\n'.join(html)


# ============================================================
# Main
# ============================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Publish markdown to Confluence')
    parser.add_argument('--config', required=True, help='Path to confluence.json config file')
    args = parser.parse_args()

    with open(args.config) as f:
        config = json.load(f)

    base_url = config['base_url']
    token = config['session_token']
    base_dir = Path(config.get('base_dir', '.'))
    diagrams_dir = base_dir / config.get('diagrams_dir', 'diagrams')

    # Track already-uploaded diagrams to avoid duplicates
    uploaded = {}

    for page_cfg in config['pages']:
        page_id = page_cfg['page_id']
        title = page_cfg['title']
        md_file = page_cfg['md_file']
        print(f"\n=== {title} (page {page_id}) ===")

        # Upload diagrams (PUT handles both new and existing attachments)
        diagram_map = {}
        for fname in page_cfg.get('diagrams', []):
            if fname in uploaded:
                cid, pid, ver = uploaded[fname]
            else:
                fpath = diagrams_dir / fname
                if not fpath.exists():
                    print(f"  WARNING: {fpath} not found")
                    continue
                result = upload_attachment(base_url, token, page_id, str(fpath))
                if not result:
                    continue
                cid, pid, ver = result
                uploaded[fname] = (cid, pid, ver)
                print(f"  Uploaded {fname} -> {cid} v{ver}")
            diagram_map[fname] = drawio_macro(cid, pid, fname, version=ver)

        # Also make already-uploaded diagrams available
        for fname, (cid, pid, ver) in uploaded.items():
            if fname not in diagram_map:
                diagram_map[fname] = drawio_macro(cid, pid, fname, version=ver)

        # Read and convert markdown
        md_path = base_dir / md_file
        if not md_path.exists():
            print(f"  SKIP: {md_path} not found")
            continue
        md_text = md_path.read_text(encoding='utf-8')
        content = convert_md(md_text, diagram_map)

        # Get version and update
        version = get_page_version(base_url, token, page_id)
        update_page(base_url, token, page_id, title, content, version + 1)

    print("\nDone!")


if __name__ == '__main__':
    main()
