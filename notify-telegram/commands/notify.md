---
description: "Send a notification message to the user via Telegram. Use when the user has asked to receive updates via Telegram, or when explicitly asked to send a Telegram message. Also use /notify-telegram:notify setup to configure credentials."
---

# Telegram Notify

Send one-way notification messages to the user via the Telegram Bot API.

## When to Use This Skill

- The user has explicitly asked to be notified via Telegram (e.g. "send me updates on Telegram", "notify me when done", "let me know on Telegram")
- The user explicitly invokes `/notify-telegram:notify`
- **NEVER auto-invoke in a new session** unless the user has asked for Telegram notifications in that session
- When in doubt, ask: "Want me to send you a Telegram notification?"

## Setup

If the config file `~/.claude/telegram.env` does not exist, or the user says "setup" or "configure", guide them through setup:

### Step 1: Create a Telegram Bot (if they don't have one)

Tell the user:

> To create a Telegram bot:
> 1. Open Telegram and search for `@BotFather`
> 2. Send `/newbot` and follow the prompts
> 3. You'll receive a bot token like `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11`
> 4. **Start a conversation with your new bot** (search for it and press "Start") — this is required before the bot can message you

### Step 2: Get the User's Chat ID (if they don't have one)

If the user doesn't know their chat ID, help them find it:

> Send any message to your bot first (e.g. "hello"), then I'll look it up.

Then run:

```bash
curl -s "https://api.telegram.org/bot${TOKEN}/getUpdates" | python3 -c "import sys,json; updates=json.load(sys.stdin)['result']; print(updates[-1]['message']['chat']['id'] if updates else 'No messages found - please send a message to your bot first')"
```

Replace `${TOKEN}` with the token the user provided.

### Step 3: Save Configuration

Create the config file:

```bash
cat > ~/.claude/telegram.env << 'EOF'
TELEGRAM_BOT_TOKEN=<token>
TELEGRAM_CHAT_ID=<chat_id>
EOF
chmod 600 ~/.claude/telegram.env
```

### Step 4: Send a Test Message

Send a test message to verify the setup works. Use the sending instructions below. The test message should be:

```
Setup complete! Telegram notifications are working.
```

After successful test, tell the user they can now ask for Telegram notifications in any session.

---

## Sending a Message

### 1. Load credentials

```bash
source ~/.claude/telegram.env
```

If the file doesn't exist, tell the user to run `/notify-telegram:notify setup` first.

### 2. Send via curl

Use this exact pattern:

```bash
source ~/.claude/telegram.env && curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -H 'Content-Type: application/json' \
  -d "$(python3 -c "
import json, sys
msg = '''MESSAGE_TEXT_HERE'''
print(json.dumps({
    'chat_id': '${TELEGRAM_CHAT_ID}',
    'text': msg,
    'parse_mode': 'HTML'
}))
")"
```

Replace `MESSAGE_TEXT_HERE` with the actual message. Using python3 for JSON encoding ensures proper escaping of special characters, quotes, and newlines.

### 3. Handle long messages

Telegram has a **4096 character limit**. If your message is longer, split it into multiple sends. Prefer summarizing over splitting.

### 4. Check the response

The API returns JSON. Check that `"ok": true` is in the response. If not, show the error to the user.

---

## Message Style Guidelines

- Keep messages concise and scannable
- Use emojis sparingly to aid visual scanning (not decoration):
  - Completion/success: use a checkmark
  - Error/failure: use a cross or warning sign
  - Info/update: use an "i" or arrow indicator
  - Waiting/in-progress: use an hourglass or spinner indicator
- Use HTML formatting lightly where helpful:
  - `<b>bold</b>` for emphasis on key terms
  - `<code>inline code</code>` for file paths, commands, variable names
  - `<pre>code block</pre>` for multi-line code output
  - `<i>italic</i>` for secondary information
- Do NOT use `<u>` underline tags
- No prefix or branding — just the message content
- Newlines work naturally (just use `\n` in the message)

### Example Messages

**Task completion:**
```
Done! Refactored the auth module.

3 files changed:
- src/auth/login.ts
- src/auth/session.ts
- src/auth/types.ts

All 42 tests passing.
```

**Error notification:**
```
Build failed in CI.

The test UserService.create is failing:
Expected 201 but got 400

Looks like the validation schema changed. I can investigate if you want.
```

**Progress update:**
```
Migration progress: 15/23 endpoints converted.

Currently working on /api/v2/orders.
No blockers so far.
```

---

## Error Handling

- If `~/.claude/telegram.env` is missing: tell user to run setup
- If curl fails or returns `"ok": false`: show the error message from the API response to the user
- Common errors:
  - "chat not found" — user hasn't started a conversation with the bot yet
  - "Unauthorized" — bot token is wrong
  - "Bad Request: can't parse entities" — HTML formatting error; retry without parse_mode
