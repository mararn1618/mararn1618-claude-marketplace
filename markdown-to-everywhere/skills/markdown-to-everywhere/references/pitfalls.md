# Pitfalls Reference

All known pitfalls from building and operating the doc pipeline.

---

## 1. Cell ID collisions in draw.io viewer

**Symptom:** `d.setId is not a function` in browser console. Diagrams fail to render.
**Cause:** Multiple draw.io diagrams on the same HTML page share a cell ID namespace. If two diagrams both have a cell `id="box1"`, the viewer crashes.
**Fix:** Always use `write_diagram()` from `drawio_helpers.py`. It prefixes every cell ID with the diagram filename automatically.

## 2. ERmany/ERone arrow markers crash viewer

**Symptom:** Same `d.setId` error, but cell IDs are unique.
**Cause:** The `viewer-static.min.js` CDN build does not include the ER shapes plugin. `ERmany`, `ERone`, `ERmandOne` markers are undefined.
**Fix:** Use standard arrows: `endArrow=classic;endFill=1;` for many-side, `startArrow=oval;startFill=0;` for one-side. Put cardinality (e.g., `1:N`) in the edge label.

## 3. Inline draw.io XML in HTML attributes

**Symptom:** `Unterminated string in JSON`, `Bad control character in JSON`, or diagrams not rendering.
**Cause:** Inlining XML in the `data-mxgraph` HTML attribute causes encoding hell. `&#10;` entities get decoded to literal newlines by the browser, breaking JSON.parse. Single quotes in `<?xml version='1.0'>` terminate the attribute.
**Fix:** Use URL-based loading: `data-mxgraph='{"url":"filename.drawio"}'`. Copy the `.drawio` file next to the HTML. The viewer fetches it via XHR.

## 4. Draw.io diagrams show spinner but never render

**Symptom:** Loading spinner appears, diagram never shows.
**Cause:** The draw.io viewer uses `XMLHttpRequest` to fetch `.drawio` files, which does not work with the `file://` protocol.
**Fix:** Serve via HTTP: `python3 -m http.server 8765` from the `html/` directory.

## 5. Raw HTML tags displayed as text in draw.io cells

**Symptom:** Cell shows literal `<b>Title</b>` instead of bold text.
**Cause:** Draw.io only interprets HTML tags when `html=1;` is in the cell's style string.
**Fix:** Include `html=1;` in every style that uses `<b>`, `<font>`, `<br>`, or other HTML tags. All styles in `drawio_helpers.py` already include this.

## 6. Dark mode SVG rendering

**Symptom:** Draw.io CLI export produces diagrams with inverted/dark backgrounds.
**Cause:** The CLI picks up system dark mode preferences.
**Fix:** Use the JavaScript viewer (CDN) for rendering instead of CLI export. The viewer always renders with the diagram's own color scheme.

## 7. Confluence CDATA section breaks

**Symptom:** Confluence page update fails or content is truncated mid-code-block.
**Cause:** `]]>` inside a code block terminates the CDATA section prematurely.
**Fix:** Escape `]]>` as `]]]]><![CDATA[>` before wrapping in CDATA. The `publish_confluence.py` script handles this automatically.

## 8. Confluence draw.io "Diagram not found"

**Symptom:** Draw.io macro on Confluence page shows "Diagram not found" error.
**Cause:** Either (a) the attachment upload did not complete before the page was updated, or (b) `contentVer`/`revision` parameters in the macro do not match the actual attachment version.
**Fix:** Upload all attachments first and verify 200 responses. For first-time uploads, use `contentVer=1` and `revision=1`. For re-uploads, read the attachment metadata to get the actual version.

## 9. Confluence 401/403 errors

**Symptom:** API calls return 401 Unauthorized or 403 Forbidden.
**Cause:** 401 means the session cookie (JWT) has expired. 403 means the XSRF bypass header is missing.
**Fix:** For 401: re-extract `tenant.session.token` from your browser (re-login if needed). For 403: add `X-Atlassian-Token: no-check` header to all POST/PUT requests.

## 10. Confluence page version conflict (409)

**Symptom:** Page update returns 409 Conflict.
**Cause:** The version number in the PUT body does not match `current_version + 1`.
**Fix:** Always GET the current version first, then increment by exactly 1 in the PUT payload. Never hardcode version numbers.

## 11. Two-column layout looks cramped or broken

**Symptom:** Diagram is squeezed, text overflows, or layout looks off.
**Cause:** Wide horizontal diagrams do not fit in a 55%/42% column split.
**Fix:** Only use two-column layouts for tall/square diagrams (ERDs, vertical flows) with 3-8 short bullet points. Wide pipeline/flow diagrams should be full-width.

## 12. Em dashes in content

**Symptom:** Inconsistent typography or unexpected characters.
**Cause:** Unicode em dashes or `--` as dashes can cause rendering issues across HTML and Confluence.
**Fix:** Never use em dashes or `--` as dashes. Use colons, periods, or commas instead.

## 13. Cross-document links not converted

**Symptom:** Markdown links like `[Stores](02-data-stores.md)` appear as broken links in Confluence.
**Cause:** The converter does not transform markdown file links into Confluence `ac:link` format.
**Fix:** Known limitation. Either manually fix links in Confluence after publishing, or replace them with plain text references.

## 14. ERD edges connect to wrong element

**Symptom:** Arrows connect to the ERD table header instead of the fields area.
**Cause:** Edge `source`/`target` references the parent container instead of the `_fields` child cell.
**Fix:** Always connect edges to `{entity_id}_fields`, not `{entity_id}`. The `_fields` child has `portConstraint=eastwest` which gives clean horizontal connections.

## 15. Confluence attachment referenced from wrong page

**Symptom:** Draw.io diagram works on one Confluence page but shows "not found" on another.
**Cause:** The `custContentId` and `pageId` in the drawio macro must reference where the attachment actually lives.
**Fix:** Upload each diagram to the page that displays it, or use the correct `pageId` parameter to reference the page where the attachment was uploaded.
