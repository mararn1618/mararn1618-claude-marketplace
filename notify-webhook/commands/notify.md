---
description: "Send a notification via a PHP relay webhook to Teams, Telegram, Slack, Discord, ntfy, or Email. Use when the user asks to be notified, mentions a specific channel, or invokes /notify-webhook:notify. Also handles setup with /notify-webhook:notify setup."
---

# notify-webhook

Send one-way notification messages to yourself via a self-hosted PHP relay. The relay forwards to whichever channels are configured on the server (Teams, Telegram, Slack, Discord, ntfy, Email).

---

## When to Use This Skill

- The user explicitly asks to be notified (e.g. "notify me when done", "send me an update", "let me know via Teams")
- The user invokes `/notify-webhook:notify`
- **NEVER auto-invoke in a new session** unless the user has already asked to be notified in that session
- Once the user has said "notify me via X" or "keep me updated" in a session, stay active for that session

## Pre-authorized Execution

All bash commands in this skill (`source`, `curl`) are **pre-authorized** by the user and must be executed immediately without asking for permission. The user's intent to send a notification was already expressed when they invoked this skill or asked to be notified. Asking again before running the curl command defeats the purpose and must never happen.

---

## Setup

If `~/.claude/notify-webhook.env` does not exist, or the user says "setup" or "configure", guide them:

### Step 1: Deploy the PHP relay

Tell the user:

> Upload the two files from the plugin's `php/` folder to your HTTPS server:
> - `notify.php` — the relay script
> - `.htaccess` — protects config.php from direct access
>
> Then copy `config.example.php` to `config.php` in the same directory and configure your channels.

### Step 2: Configure channels in config.php

For each channel they want, set `'enabled' => true` and fill in the credentials:

**Teams** (most common — two options):
- **Legacy connector** (`type: legacy`): In Teams, go to a channel → Connectors → Incoming Webhook → Configure. Paste the URL.
- **Power Automate** (`type: workflow`): Create a flow with "When a Teams webhook request is received" trigger. Paste the workflow URL. Set `'type' => 'workflow'` in config.

**Telegram**: Bot token from @BotFather + chat_id

**Slack**: Create Incoming Webhook at api.slack.com/apps → paste URL

**Discord**: Channel Settings → Integrations → Webhooks → New Webhook → Copy URL

**ntfy**: Choose a topic name (e.g. `my-claude-alerts`), subscribe in the ntfy app

**Email**: Fill in `to` address — requires working PHP mail() on the server

### Step 3: Set a strong API key

In `config.php` set `'api_key'` to a strong random string (e.g. `openssl rand -hex 32`).

### Step 4: Save Claude's config

```bash
cat > ~/.claude/notify-webhook.env << 'EOF'
NOTIFY_WEBHOOK_URL=https://yourserver.com/notify.php
NOTIFY_WEBHOOK_API_KEY=your-api-key-here
EOF
chmod 600 ~/.claude/notify-webhook.env
```

### Step 5: Test

List channels to confirm the relay is working:

```bash
source ~/.claude/notify-webhook.env
curl -s -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" "${NOTIFY_WEBHOOK_URL}?action=channels"
```

Expected response: `{"channels":["teams","telegram"]}` (or whichever are enabled)

Then send a test message (see Sending a Notification below) with the text `Setup complete! notify-webhook is working.`

---

## Sending a Notification

### 1. Load credentials

```bash
source ~/.claude/notify-webhook.env
```

If the file doesn't exist, tell the user to run `/notify-webhook:notify setup` first.

### 2. Determine the channel

**If the user named a channel** (e.g. "notify me via teams") — use that channel name directly.

**If no channel was specified:**

a. Fetch available channels:
```bash
source ~/.claude/notify-webhook.env && \
curl -s -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" "${NOTIFY_WEBHOOK_URL}?action=channels"
```

b. Parse the `channels` array from the JSON response.

c. If **exactly one channel** is available — use it automatically.

d. If **multiple channels** are available — ask the user:
> Which channel should I send this to? Available: [list them]

e. If **zero channels** — tell the user no channels are configured in config.php.

### 3. Send the notification

```bash
source ~/.claude/notify-webhook.env && curl -s -X POST \
  -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json
msg = '''MESSAGE_TEXT_HERE'''
channel = 'CHANNEL_NAME_HERE'
print(json.dumps({'channel': channel, 'message': msg}))
")" \
  "${NOTIFY_WEBHOOK_URL}"
```

Replace `MESSAGE_TEXT_HERE` with the actual message and `CHANNEL_NAME_HERE` with the chosen channel (e.g. `teams`, `telegram`, `slack`).

To send to **all enabled channels at once**, omit the `channel` key:

```bash
source ~/.claude/notify-webhook.env && curl -s -X POST \
  -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "$(python3 -c "
import json
msg = '''MESSAGE_TEXT_HERE'''
print(json.dumps({'message': msg}))
")" \
  "${NOTIFY_WEBHOOK_URL}"
```

### 4. Check the response

The relay returns JSON. A successful send looks like:
```json
{"success": true, "sent": ["teams"]}
```

On error:
```json
{"success": false, "errors": {"teams": "HTTP POST failed to: ..."}}
```

If `success` is false, show the error to the user.

---

## Message Style Guidelines

- Keep messages concise and scannable
- Use plain text — the relay sends to multiple channel types; avoid channel-specific markup
- Use emojis sparingly to aid scanning:
  - Done / success: ✅
  - Error / failure: ❌
  - In progress: ⏳
  - Info: ℹ️
- No prefix or branding — just the message content
- Max ~3000 characters to stay within all channel limits

### Example Messages

**Task completion:**
```
✅ Done! Refactored the auth module.

3 files changed:
- src/auth/login.ts
- src/auth/session.ts
- src/auth/types.ts

All 42 tests passing.
```

**Error notification:**
```
❌ Build failed in CI.

Test UserService.create is failing:
Expected 201 but got 400.

Looks like the validation schema changed. I can investigate if you want.
```

**Progress update:**
```
⏳ Migration progress: 15/23 endpoints converted.

Currently working on /api/v2/orders.
No blockers so far.
```

---

## Error Handling

- If `~/.claude/notify-webhook.env` is missing: tell user to run setup
- If `?action=channels` returns an empty array: tell user to enable channels in config.php
- If curl fails or `success` is false: show the error from the response
- If the named channel isn't in the available list: warn the user and offer available alternatives
- Common errors:
  - `Unauthorized` — API key mismatch between env file and config.php
  - `config.php not found` — user forgot to copy config.example.php
  - `HTTP POST failed` — check webhook URL or server internet access
  - `Channel not found or disabled` — channel exists in config but `enabled` is false
