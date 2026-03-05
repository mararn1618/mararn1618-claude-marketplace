#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="$HOME/.claude/notify-webhook.env"
if [[ ! -f "$ENV_FILE" ]]; then
  echo '{"error":"~/.claude/notify-webhook.env not found. Run: /notify-webhook:notify setup"}' >&2
  exit 1
fi
source "$ENV_FILE"

case "${1:-}" in
  channels)
    curl -s -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" \
      "${NOTIFY_WEBHOOK_URL}?action=channels"
    ;;
  send)
    channel="${2:?Usage: notify-webhook.sh send <channel> <message>}"
    message="${3:?Usage: notify-webhook.sh send <channel> <message>}"
    python3 -c "import json,sys;print(json.dumps({'channel':sys.argv[1],'message':sys.argv[2]}))" \
      "$channel" "$message" | \
    curl -s -X POST \
      -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" \
      -H "Content-Type: application/json" \
      -d @- \
      "${NOTIFY_WEBHOOK_URL}"
    ;;
  send-all)
    message="${2:?Usage: notify-webhook.sh send-all <message>}"
    python3 -c "import json,sys;print(json.dumps({'message':sys.argv[1]}))" \
      "$message" | \
    curl -s -X POST \
      -H "X-API-Key: ${NOTIFY_WEBHOOK_API_KEY}" \
      -H "Content-Type: application/json" \
      -d @- \
      "${NOTIFY_WEBHOOK_URL}"
    ;;
  *)
    cat >&2 <<'USAGE'
Usage: notify-webhook.sh <command> [args...]

Commands:
  channels                    List available channels
  send <channel> <message>    Send to a specific channel
  send-all <message>          Send to all enabled channels
USAGE
    exit 1
    ;;
esac
