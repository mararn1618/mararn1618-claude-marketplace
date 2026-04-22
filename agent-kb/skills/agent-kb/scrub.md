# Scrub Operation

Scan all files in the knowledge base for sensitive data. Produces a report for the user to review. Does not auto-redact.

This operation runs automatically at the end of a `build`. It is not a standalone subcommand.

---

## Step 1: Ask for Confirmation

Before scanning, present the default scrub categories and ask the user:

```
## Sensitive Data Scrub

The KB is built. Before you share it, I can scan for sensitive data.

Default categories I'll check:
  1. Filesystem paths (/Users/..., ~/..., C:\...)
  2. Internal URLs (Confluence, Jira, SharePoint, localhost, intranet)
  3. Person names (full first + last names)
  4. Credentials (API keys, tokens, passwords, connection strings)
  5. Email addresses
  6. IP addresses (internal ranges, specific server IPs)
  7. Phone numbers
  8. Proprietary identifiers (customer IDs, account numbers, ticket IDs)

Based on your KB's domain, I'd also suggest checking for:
  <brainstorm 2-4 additional categories specific to the KB's content, e.g.:
   - "SAP system IDs and client numbers" for an SAP-related KB
   - "Patient identifiers" for a healthcare KB
   - "AWS account IDs and ARNs" for a cloud-infra KB>

Run the scrub? You can add/remove categories, or skip entirely.
```

If the user says skip, print "Scrub skipped." and return to the build report (Step 7 of build.md).

If the user confirms (with or without modifications), proceed with the confirmed category list.

---

## Step 2: Scan Files (PARALLEL)

Find all `.md` files in the KB target directory using Glob (`**/*.md`), excluding `CLAUDE.md` and `AGENTS.md`.

Split the file list into groups of roughly equal size, one group per sub-agent. Use **3-5 sub-agents** depending on the total file count:
- Under 10 files: 2 sub-agents
- 10-30 files: 3 sub-agents
- 30-60 files: 4 sub-agents
- Over 60 files: 5 sub-agents

Spawn all sub-agents in a **single message** so they run concurrently.

Each sub-agent receives:

```
You are a sensitive data scanner for a knowledge base.

Your assigned files:
<list of absolute file paths>

Categories to check:
<numbered list of confirmed categories from Step 1>

Instructions:
1. Read each file.
2. For each file, scan for matches against the categories. Use your judgment as a language model to identify sensitive data in context (especially person names in meeting notes, stakeholder lists, attribution lines) rather than relying solely on regex patterns.
3. For each finding, record:
   - File path
   - Line number (or approximate location)
   - Category matched
   - The sensitive fragment (truncated to 80 chars if longer)
   - Severity: HIGH (credentials, passwords), MEDIUM (names, emails, IPs), LOW (filesystem paths, internal URLs)
4. Return findings as a structured list:

## Findings

| File | Line | Category | Fragment | Severity |
|------|------|----------|----------|----------|
| path/to/file.md | 23 | Credentials | `Bearer sk-proj-abc...` | HIGH |
| path/to/file.md | 45 | Person name | `John Smith` | MEDIUM |

If no findings for your file set, return: "No sensitive data found in <N> files."
```

Sub-agent configuration:
- `model: "opus"` (accurate pattern matching matters)
- `allowed-tools: Read, Glob, Grep`
- Give each agent a name like `scrubber-1`, `scrubber-2`, etc.

---

## Step 3: Compile Report

Merge all sub-agent findings into a single report, sorted by severity (HIGH first), then by file path.

If zero findings across all scanners, report: "No sensitive data found across N files. The KB is clean." Skip the redaction options and return to the build report (Step 7 of build.md).

Otherwise, present to the user:

```
## Scrub Report

Scanned: <N> files across <M> domain folders
Findings: <total count> (<HIGH count> high, <MEDIUM count> medium, <LOW count> low)

### HIGH severity
| File | Line | Category | Fragment |
|------|------|----------|----------|
| ... | ... | ... | ... |

### MEDIUM severity
| File | Line | Category | Fragment |
|------|------|----------|----------|
| ... | ... | ... | ... |

### LOW severity
| File | Line | Category | Fragment |
|------|------|----------|----------|
| ... | ... | ... | ... |

### No findings
<list of clean files, if any>

What would you like to do?
  1. Redact specific findings (tell me which ones)
  2. Redact all findings in a severity tier
  3. Keep as-is (no redaction)
  4. I'll handle it manually
```

---

## Step 4: Apply Redactions (if requested)

If the user asks to redact:

- Replace sensitive fragments with a placeholder: `[REDACTED:<category>]`
  - Example: `Bearer sk-proj-abc...` becomes `[REDACTED:credential]`
  - Example: `John Smith` becomes `[REDACTED:name]`
  - Example: `/Users/john/Documents/secret` becomes `[REDACTED:path]`
- Use the Edit tool for surgical replacements. Do not rewrite entire files.
- After all redactions, re-run a quick verification scan (no sub-agents needed, just grep for the original fragments) to confirm they are gone.
- Report: "Redacted <N> findings across <M> files."

If the user says they'll handle it manually, print: "Scrub report above for your reference. No changes made." and stop.

---

## Important Rules

- Never auto-redact without user confirmation. The scrub is advisory.
- Never modify CLAUDE.md or AGENTS.md during scrub (only article files).
- Truncate displayed fragments to 80 characters to avoid leaking full secrets in the report.
- HIGH severity findings should always be called out prominently, even if the user asked for a summary view.
