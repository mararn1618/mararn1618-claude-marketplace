# Markdown Authoring Conventions

Rules and patterns for writing architecture documentation that renders correctly across HTML and Confluence.

---

## Document Structure

### File naming

Files follow the `NN-topic.md` pattern where NN is the reading order:
```
00-overview.md
01-pipeline-model.md
02-data-stores.md
...
```

The `render_html.py` script auto-discovers files matching this pattern and builds the navigation bar from them.

### Target length

Each document should be 100-180 lines. Focused on one topic. If a document grows beyond ~200 lines, consider splitting.

### Sections

- **H1** (`# Title`): Page title. Skipped during body conversion (set via page title in HTML/Confluence).
- **H2** (`## Section`): Major sections. Always tagged with a status badge.
- **H3** (`### Subsection`): Subsections within an H2.
- **`---`**: Horizontal rule between major H2 sections.

---

## Status Badges

Every H2 section header is tagged with a status badge indicating whether the content is existing, new, or changed relative to the current system.

### Primary badges

| Token | Meaning | HTML Color | Confluence Color |
|-------|---------|-----------|-----------------|
| `[EXISTING]` | Already in production | Green | Green |
| `[NEW]` | Proposed by this architecture | Blue | Blue |
| `[CHANGED]` | Existing with proposed modifications | Amber | Yellow |
| `[GREENFIELD]` | Must be built from scratch | Blue | Red |
| `[REVISED]` | Recently revised | Amber | Yellow |

### Compound badges

| Token | Renders as |
|-------|-----------|
| `[NEW: GREENFIELD]` | Two badges: NEW + GREENFIELD |
| `[EXISTING/CHANGED]` | Two badges: EXISTING + CHANGED |

### Usage in headers

```markdown
## Config Data Model [EXISTING]
## 3-Stage Pipeline [NEW]
## Scheduling Rework [CHANGED]
## Inbound Processing [NEW: GREENFIELD]
```

### Usage in tables

Badges also work inside table cells:

```markdown
| Store | Status |
|-------|--------|
| Inbox | [EXISTING] |
| Normalized Outbound | [NEW] |
```

---

## Two-Column Layouts

Side-by-side content using HTML comment markers:

```markdown
<!-- columns -->
![Config ERD](diagrams/10-config-erd.drawio)

<!-- col -->
**Key tables:**
- `parties`: Partner registry
- `channels`: Endpoint configuration
- `files`: File definitions
<!-- /columns -->
```

### When to use

**Good candidates:**
- Tall/square diagram (ERD, vertical flow) + 3-8 short bullet points
- Two parallel lists (In Scope / Out of Scope)

**Bad candidates:**
- Wide horizontal diagrams (pipelines, timelines) - they get squeezed
- Diagram + long paragraph text
- Diagram + tables
- Pages without diagrams

### CSS behavior

- HTML: 55% diagram / 42% text, responsive collapse below 768px
- Confluence: `ac:layout-section type="two_equal"` (50/50 split)

---

## Diagram References

Embed draw.io diagrams using standard markdown image syntax:

```markdown
![Outbound Pipeline](diagrams/03-outbound-pipeline.drawio)
```

- The **caption** (alt text) becomes a subtitle below the diagram in HTML
- The `.drawio` file is copied to `html/` during rendering and loaded interactively by the viewer
- Multiple diagrams per page are supported (cell ID prefixing prevents collisions)
- Diagrams must be in a `diagrams/` subdirectory relative to the markdown files

---

## "Concept: Why..." Pattern

Every `[NEW]` component should include a section explaining the problem it solves:

```markdown
## Concept: Why Separate Stores? [NEW]

**The problem:** Today, there is no record-level audit trail. If a regulator asks
"which reports included item X?", the only way to answer is to re-process every
historical file.

**The solution:** Four platform-owned stores, each capturing a different stage.
The two new normalized stores add record-level JSON audit snapshots.
```

This pattern ensures architecture decisions are justified, not just described.

---

## Footer Navigation

Every document ends with a navigation footer linking all pages:

```markdown
[Overview](00-overview.md) | **[Pipeline](01-pipeline-model.md)** | [Stores](02-data-stores.md) | ...
```

The current page is bold. This footer is:
- **Stripped** by the Confluence converter (Confluence has its own navigation)
- **Ignored** by the HTML renderer (which generates its own nav bar)

---

## Code Blocks

Use fenced code blocks with language hints:

````markdown
```sql
SELECT n.loan_number, n.entity_type
FROM normalized_out n
WHERE n.loan_number = 'X-12345'
```
````

Supported language hints: `sql`, `python`, `bash`, `xml`, `json`, or no hint for pseudocode/class hierarchies.

---

## Content Rules

- **No em dashes** or `--` as dashes. Use colons, periods, commas.
- **No people names** in architecture docs. Use role/team references (e.g., "product management directive" not "John's directive").
- **Keep table names and class names** as developer anchors (e.g., `/app/config_table`, `BaseProcessor`).
- **Mid-ground tone**: accessible to management, precise enough for developers.
