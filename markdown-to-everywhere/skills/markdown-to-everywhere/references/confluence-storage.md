# Confluence Publishing Reference

Complete API reference and storage format guide for publishing to Confluence Cloud.

---

## Authentication

Confluence Cloud uses session-based authentication via the `tenant.session.token` cookie.

### Getting the token

1. Open your Confluence instance in a browser and log in (SSO, Google, etc.)
2. Extract the cookie:
   - **Browser DevTools**: Application > Cookies > find `tenant.session.token`
   - **Playwright**: `playwright-cli run-code "async page => { const c = await page.context().cookies(); return c.find(x => x.name === 'tenant.session.token')?.value; }"`
3. The token is a JWT that expires periodically (typically hours). If API calls return 401, re-extract.

### Using the token

Every API call includes:
```
Cookie: tenant.session.token={jwt}
```

Write operations (POST, PUT) also need XSRF bypass:
```
X-Atlassian-Token: no-check
```

---

## API Endpoints

### Upload attachment

```
PUT https://{tenant}.atlassian.net/wiki/rest/api/content/{pageId}/child/attachment
Headers:
  Cookie: tenant.session.token={jwt}
  X-Atlassian-Token: no-check
Body: multipart/form-data
  file: @path/to/file.drawio (type=application/xml)
  minorEdit: true
```

Use `PUT` (not `POST`). PUT handles both new and existing attachments. POST returns 400 if an attachment with the same filename already exists.

Response: `results[0].id` = attachment content ID (strip `att` prefix for macro use). `results[0].version.number` = version (needed for draw.io macro `contentVer`/`revision` params).

### Get page version

```
GET https://{tenant}.atlassian.net/wiki/api/v2/pages/{pageId}
Headers:
  Cookie: tenant.session.token={jwt}
  Accept: application/json
```

Response: `version.number` = current version (increment by 1 for update).

### Update page content

```
PUT https://{tenant}.atlassian.net/wiki/rest/api/content/{pageId}
Headers:
  Cookie: tenant.session.token={jwt}
  Content-Type: application/json
  X-Atlassian-Token: no-check
Body:
{
  "id": "{pageId}",
  "type": "page",
  "title": "Page Title",
  "version": {"number": currentVersion + 1},
  "body": {
    "storage": {
      "value": "<confluence storage format XHTML>",
      "representation": "storage"
    }
  }
}
```

### List child pages

```
GET https://{tenant}.atlassian.net/wiki/rest/api/content/{parentPageId}/child/page?limit=50
```

---

## Confluence Storage Format Elements

### Status badges

```xml
<ac:structured-macro ac:name="status" ac:schema-version="1">
  <ac:parameter ac:name="title">NEW</ac:parameter>
  <ac:parameter ac:name="colour">Blue</ac:parameter>
</ac:structured-macro>
```

Color mapping:
| Badge | Colour parameter |
|-------|-----------------|
| NEW | Blue |
| EXISTING | Green |
| CHANGED | Yellow |
| GREENFIELD | Red |
| REVISED | Yellow |

### Draw.io diagram (embedded from attachment)

```xml
<ac:structured-macro ac:name="drawio" ac:schema-version="1" data-layout="default">
  <ac:parameter ac:name="mVer">2</ac:parameter>
  <ac:parameter ac:name="zoom">1</ac:parameter>
  <ac:parameter ac:name="simple">0</ac:parameter>
  <ac:parameter ac:name="inComment">0</ac:parameter>
  <ac:parameter ac:name="custContentId">{attachment_numeric_id}</ac:parameter>
  <ac:parameter ac:name="pageId">{page_id_where_attachment_lives}</ac:parameter>
  <ac:parameter ac:name="lbox">1</ac:parameter>
  <ac:parameter ac:name="diagramDisplayName">{filename.drawio}</ac:parameter>
  <ac:parameter ac:name="contentVer">1</ac:parameter>
  <ac:parameter ac:name="revision">1</ac:parameter>
  <ac:parameter ac:name="baseUrl">https://{tenant}.atlassian.net/wiki</ac:parameter>
  <ac:parameter ac:name="diagramName">{filename.drawio}</ac:parameter>
  <ac:parameter ac:name="pCenter">0</ac:parameter>
  <ac:parameter ac:name="width">{width, e.g. 900}</ac:parameter>
  <ac:parameter ac:name="links" />
  <ac:parameter ac:name="tbstyle" />
  <ac:parameter ac:name="height">{height, e.g. 340}</ac:parameter>
</ac:structured-macro>
```

### Two-column layout

```xml
<ac:layout>
  <ac:layout-section ac:type="two_equal" ac:breakout-mode="default">
    <ac:layout-cell>{left column content}</ac:layout-cell>
    <ac:layout-cell>{right column content}</ac:layout-cell>
  </ac:layout-section>
</ac:layout>
```

### Code block

```xml
<ac:structured-macro ac:name="code" ac:schema-version="1">
  <ac:parameter ac:name="language">sql</ac:parameter>
  <ac:plain-text-body><![CDATA[SELECT * FROM table]]></ac:plain-text-body>
</ac:structured-macro>
```

Escape `]]>` inside code as `]]]]><![CDATA[>`.

### Note / callout (from blockquotes)

```xml
<ac:structured-macro ac:name="note" ac:schema-version="1">
  <ac:rich-text-body><p>Important information here.</p></ac:rich-text-body>
</ac:structured-macro>
```

### Standard HTML elements

All these are valid in Confluence storage format:

| Element | Use | Notes |
|---------|-----|-------|
| `<h2>` through `<h4>` | Headings | H1 is the page title (set via API) |
| `<p>` | Paragraphs | All text should be wrapped |
| `<strong>` | Bold | |
| `<em>` | Italic | |
| `<code>` | Inline code | HTML-escape content |
| `<ol>`, `<ul>` | Lists | Each `<li>` must contain `<p>` |
| `<table>`, `<tbody>` | Tables | No `<thead>` in Confluence storage |
| `<tr>`, `<th>`, `<td>` | Table cells | Each cell must contain `<p>` |
| `<hr/>` | Horizontal rule | |

### Cross-page links (manual)

```xml
<ac:link>
  <ri:page ri:content-title="Target Page Title" ri:space-key="SPACEKEY"/>
  <ac:plain-text-link-body><![CDATA[link text]]></ac:plain-text-link-body>
</ac:link>
```

This is not auto-generated from markdown `[text](file.md)` links. Known limitation.

---

## Markdown to Storage Format Conversion

The converter in `publish_confluence.py` processes markdown line-by-line with this priority:

1. Two-column markers (`<!-- columns/col/columns -->`)
2. Navigation footer (lines matching `[text](file.md) |` pattern, stripped)
3. H1 (skipped, page title set via API)
4. H2/H3/H4 (with inline badge substitution)
5. Horizontal rules (`---`)
6. Blockquotes (`>` prefix, converted to note macro)
7. Fenced code blocks (with language parameter)
8. Diagram references (`![](diagrams/*.drawio)`)
9. Tables (header + separator + body rows)
10. Ordered lists
11. Unordered lists
12. Blank lines (skipped)
13. Regular paragraphs

Badge substitution happens inside `inline()` and matches longest tokens first to prevent `[NEW: GREENFIELD]` from being partially matched as `[NEW]`.
