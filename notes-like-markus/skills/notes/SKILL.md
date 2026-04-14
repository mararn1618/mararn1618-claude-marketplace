---
description: "Produce terse, human-voice notes (fleeting daily notes, meeting alignments, ticket scratchpads, test lists, research docs, daily summaries) instead of verbose AI deliverables. Use this skill whenever the user says things like 'write this as a note like I would', 'fleeting note for the meeting', 'prep note for tomorrow', 'make this a meeting note', 'jot this down', 'put this in my Obsidian vault', or when they explicitly invoke /notes-like-markus or /notes-like-markus:notes. Output shape is fragmentary bullets, lowercase starts, deep links inline, no framing prose, no executive summaries, no em dashes."
---

# notes-like-markus

A style reference for producing human-shaped notes. When invoked, the agent drops its default deliverable voice (headers, framing prose, executive summaries, parallel bullets, hedging) and writes the way a busy engineer scribbles into their daily Obsidian page: fragmentary, lowercase, deep-linked, shaped by the content rather than by a template.

This skill shapes note content only. It does not pick file paths, does not write to specific vault locations, and does not distinguish machines. Hand it the material, it hands back note-shaped text.

## Style rules

1. Fragmentary bullets over prose. Keywords and short phrases, not paragraphs. No diploma-thesis walls of text. The reason to take a note is to compress, so leaning into compression is the whole point.
2. Light headings are fine, even encouraged for organization. One or two H2s per note is normal. Do not stack three levels deep, do not put a header on every two-line paragraph, and do not build a table of contents. Most structure comes from indentation depth, not from heading hierarchy.
3. Indent nested bullets with 4 spaces per level. Spaces only, no tabs. Each nesting level adds exactly 4 more spaces before the `-`. Example:

    ```
    - top level item
        - second level, 4 spaces before the dash
        - another second level
            - third level, 8 spaces before the dash
            - another third level
    - next top level item
    ```

    Why: Obsidian renders 2-space nesting as cramped, barely-offset sub-bullets. 4-space nesting gives clear visual hierarchy you can skim, and it survives round-trips through other markdown renderers without collapsing. Do not mix 2-space and 4-space indentation in the same file. Do not use tabs, since Obsidian renders tabs inconsistently depending on the tab-width setting. Leave a blank line between top-level bullet groups only when marking a section break, not between every bullet.
4. Lowercase sentence starts, terse, sentence fragments welcome. The note is a scratchpad for one person, not a press release.
5. Concrete inline, with deep links. Drop links, IDs, paths, and snippets where they belong. Not just top-level URLs: link to the specific PR, line range, comment, section, revision. Inline in the bullet, not collected at the bottom. No "see links below".
6. Visual marks allowed: `---` as a horizontal rule between unrelated chunks, `===== separator =====` as a heavier visual break when something bigger is needed, `->` as a flow arrow inside a bullet. These earn their keep because they are quick to type and read at a glance.
7. No em dashes anywhere. Not the unicode long dash, not the double-hyphen rendering. Use commas, parentheses, colons, or a period into two sentences. Em dashes are the single strongest AI-writing tell and this skill rejects them outright.
8. No AI tells. No "comprehensive overview", no executive summary preamble, no table of contents, no hedging ("it should be noted that"), no stacked bold sub-labels on every bullet, no timestamps in parentheses per section, no framing prose ("This is the doc where..."), no quote-block for user-spoken lines, no suspiciously parallel bullet structures, no emoji in headers. Each of these is a reader-speed tax with no information payoff.
9. Variable shape by purpose. Fleeting notes are raw and fragmentary. Research and ticket docs can earn more structure (tables, SQL blocks, summary or recommendation chunks), but only when the content actually warrants it. Structure is earned, not templated.
10. Frontmatter only when it earns its place. A ticket scratchpad can use `tags: [ticket]` so it shows up in a vault query. A meeting fleeting note gets no frontmatter at all.
11. The note is for future-self first. Half-thoughts, open questions, and personal asides belong in the note. It is a tool for the author, not a formal deliverable for an audience.

## Filter-out

Loose variants of the rules above appear in raw handwritten notes. They are speed artifacts, not taught style, and agent output should not copy them.

1. Typos and keyboard slips are not style. A handwritten fleeting note sometimes has them because the writer was in a hurry. Agent output has no such excuse. The relaxed feel comes from brevity and lowercase, not from misspelling.
2. No dangling section labels. A label like `Conclusion:` followed by a blank line is an in-progress scratchpad marker, not a finished-note style. Finish the one sentence that is actually known, or mark the section `(open)` or `tbd`, or leave the section out.
3. Hold one capitalization convention within a single note. Do not drift between lowercase and title case for the same entity in the same file. Cross-note looseness is fine, in-note inconsistency is noise.
4. One blank line between sections is enough. Not three or four. Blank-line padding just adds scroll.
5. Do not err too terse to be understood. A fragment like "done" is fine next to a ticket link because the link anchors it. Standalone, "done" leaves a future reader guessing. When the note will outlive the session, lean slightly fuller.
6. No `>>` emphasis arrows and no `//` inline-comment sigils. These were proposed as style and explicitly rejected. For emphasis, use bold or promote the thought to its own bullet. For asides, use a parenthetical or a colon.

## Good examples

Five short imaginary examples, one per canonical shape. All projects, people, URLs, and ticket IDs are invented.

### 1. Fleeting daily notes

```
project_falcon
- finished the webhook retry loop
    - PR: https://github.com/acme/billing-relay/pull/482#pullrequestreview-2218817
    - review sitting with anna
    - next: make jitter tunable
        - currently fixed 30s
        - per-tenant knob lives in TenantConfig
- cutover plan meeting (internal)
    - agreed to cut thursday night
    - rollback path: old ingester
    - runbook: https://wiki.acme.internal/runbooks/cutover-2026-q2#section-rollback
    - ---
    - also discussed noise in the error channel
        - most alerts are self-healed
        - proposed filter is too aggressive, risk of masking real incidents
    - open: who owns the filter rollout, anna or theo


project_griffin
- bruno collection for the billing api
    - 212 endpoints documented
    - still no fixtures, blocks load test
    - follow-up ticket: https://linear.acme.internal/GRF-441
    - ---
- chat with raj about their q2 plan
    - wants the model to write mapping rules
    - never used ai before
    - assumes gpt-class is deterministic
    - explained: no
    - action: share the prompt caching writeup before next sync
```

### 2. Meeting alignment note

```
alignment with lila on project_hydra ingest rewrite
- goal: swap the old python ingester for the rust one by end of sprint
- scope
    - only the file-drop path, not the kafka path
    - kafka path stays on the old service for now, risk of reordering
- blockers
    - auth token rotation still manual, lila filing the jira for automation
    - staging bucket acl differs from prod, see https://jira.acme.internal/FAL-102
- action items
    - me: wire the new ingester into the staging pipeline by wed
    - lila: reach out to the platform team about the acl drift
    - both: rerun the soak test once staging parity is back
- open
    - do we ship behind a flag or cut over in one step
    - decision parked until thursday standup
```

### 3. Test list / ticket checklist

```
test day 2026-03-18
- project_falcon smoke
    - https://linear.acme.internal/FAL-771 (login flow) -> done
    - https://linear.acme.internal/FAL-772 (password reset) -> done
    - https://linear.acme.internal/FAL-773 (session expiry) -> executed 1 of 3 cases, second case flakes
- project_griffin regression
    - https://linear.acme.internal/GRF-512 (billing webhook replay) -> blocked, staging down
    - https://linear.acme.internal/GRF-513 (invoice pdf render) -> done
    - https://linear.acme.internal/GRF-514 (currency rounding on eur) -> open, reproduces only with > 1m line items
- ===== separator =====
- followups for tomorrow
    - rerun FAL-773 after the flake fix lands
    - pull raj in on GRF-514, rounding lives in his helper
```

### 4. Ticket research scratchpad

```
---
tags: [ticket]
---

GRF-441: bruno fixtures missing for the billing api

- symptom: load test cannot run, collection has 212 endpoints but zero fixtures
- scope check
    - how many of the 212 actually need non-trivial fixtures

```sql
select endpoint_id, method, path
from bruno_metadata.endpoints
where collection = 'billing'
  and requires_body = true
order by path;
```

- rough count from the query above: 74 endpoints need request bodies
- the other 138 are GETs with path params only, trivial to seed
- fixture owners (who authored the original endpoint)

| endpoint group     | count | author  | status               |
|--------------------|-------|---------|----------------------|
| /invoices/*        | 22    | raj     | willing, needs a day |
| /customers/*       | 18    | sam     | on pto until friday  |
| /payments/*        | 19    | anna    | yes, has stubs ready |
| /webhooks/*        | 15    | unowned | needs triage         |

- summary
    - 74 endpoints gated, split across 4 authors, 1 unowned bucket
    - webhooks bucket is the real blocker, 15 endpoints with no owner
- recommendation
    - file a sub-ticket for the webhooks bucket and assign to project_hydra crew (they touched that code last)
    - anna's stubs can unblock payments this week, ask her to push to the shared fixtures repo
    - raj can pick up invoices once he is back from the cutover
- open
    - whether the fixture format should match the prod payload shape or the minimal shape, ask the load-test team
```

### 5. Semi-structured daily summary

```
2026-04-02 daily

## work
- project_ibex onboarding doc draft
    - first pass landed, https://github.com/northwind/platform-docs/pull/311
    - review from sam: tighten the glossary, remove the duplicated diagram
- project_falcon
    - jitter knob PR merged, https://github.com/acme/billing-relay/pull/489
    - rolled out to tenant_a and tenant_b, metrics look flat (good)
- project_griffin
    - rounding bug reproduces only above 1m line items, GRF-514 updated with a minimal repro

## meetings
- 10:00 alignment with theo on the q2 roadmap
    - agreed: ingest rewrite is p0, reporting rewrite is p2
    - parked: mobile push notifications, revisit in may
- 14:30 pairing with anna on the webhook filter
    - walked through the false-positive list
    - narrowed the filter, removed 3 over-broad rules
    - follow-up: watch the error channel for a week, then tighten again

## personal
- remember to book the dentist
- kitchen faucet still drips, call the landlord
```

## Bad counterexample

The shape to avoid. The same facts as example 1, dressed up as an AI deliverable.

```
# Daily Development Update: Tuesday, April 14, 2026

## Executive Summary

This document provides a comprehensive overview of today's development activities across the Project Falcon and Project Griffin workstreams. Key highlights include significant progress on the webhook retry loop implementation, alignment achieved regarding the upcoming production cutover, and important strategic discussions concerning the Q2 AI initiative with our partner team.

## Table of Contents

1. Project Falcon Updates
2. Project Griffin Updates
3. Key Takeaways
4. Next Steps

## 1. Project Falcon Updates

### 1.1 Webhook Retry Loop Implementation

**Status:** Completed

**Description:**
The webhook retry loop implementation has been successfully completed and is currently in the review phase. This represents a significant milestone in our ongoing efforts to improve system reliability and ensure robust handling of transient failures in downstream integrations.

**Current State:**
- Pull request submitted
- Under review by Anna (Senior Engineer)
- Estimated merge: End of week

**Identified Improvement Opportunities:**
- It should be noted that the current jitter value is hardcoded to 30 seconds
- It may be worth considering making this value configurable on a per-tenant basis
- This would allow for greater flexibility in handling tenant-specific requirements

### 1.2 Production Cutover Meeting

**Status:** Alignment Achieved

**Meeting Participants:** Development Team (internal)

**Key Decisions:**
1. Cutover Schedule: Thursday evening
2. Rollback Strategy: Legacy ingester service
3. Communication Plan: To be finalized

**Discussion Points:**
Additionally, the team touched upon concerns regarding error channel noise levels and the proposed filtering strategy.

## Key Takeaways

- Webhook retry loop is on track for completion
- Alignment achieved on cutover strategy
- Productive discussions with partner team
- Some open questions remain regarding AI strategy feasibility
```

Same facts as example 1, roughly double the length, topic names repeated three times before getting to anything concrete, two real insights (tunable jitter, cutover schedule) buried under structural scaffolding. AI tells everywhere. Half the reading speed, less information density.

## AI tells to scrub

After drafting a note, do one fast final pass for these patterns. They are the most common residue of the default deliverable voice leaking into note output.

1. AI vocab words. Replace `delve`, `pivotal`, `testament`, `showcase`, `tapestry`, `landscape` (used abstractly), `vibrant`, `intricate`, `underscore`, `foster`, `crucial`, `garner`, `additionally`, `align with` with plain words.
2. Copula avoidance. Replace `serves as`, `stands as`, `represents`, `functions as` with `is`, `are`, or `has`.
3. Negative parallelisms. Cut `not only X but Y` and `it's not just about X, it's Y` down to one clean statement.
4. Rule of three. Ideas forced into triples for rhythm. Cut to the actual count, two is fine, four is fine.
5. Persuasive-authority framing. Strip `at its core`, `the real question is`, `what really matters`, `the deeper issue`. Keep the claim, drop the framing.
6. Signposting. Do the thing instead of announcing it. Delete `let's dive in`, `here's what you need to know`, `now let's look at`.
7. Fragmented headers. A one-line warmup paragraph right after a heading that just restates the heading. Delete the warmup.
8. Inline-header vertical lists. Bullets that start with `**Label:**` and then restate the label in the body. Collapse to plain bullets or short prose.

Full 29-pattern reference: https://github.com/blader/humanizer

This skill does not implement the full humanizer taxonomy, the voice-calibration feature, or the self-critique loop. This is a compact final-pass checklist, not a general-purpose editor.
