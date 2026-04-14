---
description: "Turn any folder into a stateless, resumable Claude workspace. Scaffold CLAUDE.md + _archive/, create per-topic workstream folders with README/worklog/decisions/context/input, enforce write-to-disk discipline so sessions are interchangeable, and archive stale workstreams with user confirmation."
---

# Workstreams — Stateless, Resumable Work in a Folder

This skill turns a folder into a place where Claude can work on long-lived topics without depending on session context. Each topic ("workstream") is its own subfolder with a worklog, decision log, README, and dated inputs. A top-level `CLAUDE.md` lists all workstreams and forces every fresh session to load this skill before responding. If the session dies, a new one can pick up from disk alone.

## When to use this skill

- You are in a folder that already contains a `CLAUDE.md` gate pointing at this skill. The gate is mandatory — you must follow the runtime protocol below.
- The user asks you to scaffold a new workstreams folder.
- The user asks to start, resume, switch, or archive a workstream.
- The user hands over an input file (transcript, email, screenshot, etc.) in a workstreams folder — it must be saved per the input rules below.

## When NOT to use

- Trivial one-off questions or chitchat in a workstreams folder — skip the workstream logic, answer directly. Do not create a workstream for "what time is it".
- Folders that do not contain a `CLAUDE.md` gate pointing at this skill. Do not unilaterally scaffold — ask first.
