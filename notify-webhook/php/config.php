<?php
/**
 * notify-webhook relay — configuration
 *
 * Copy this file to config.php in the same directory and fill in your values.
 * config.php is blocked from direct HTTP access by .htaccess.
 *
 * Set 'enabled' => true for every channel you want active.
 * The Claude skill will discover all enabled channels automatically.
 */
return [

    // Must match NOTIFY_WEBHOOK_API_KEY in ~/.claude/notify-webhook.env
    'api_key' => 'change-me-to-a-strong-random-string',

    'channels' => [

        // ── Microsoft Teams ──────────────────────────────────────────────────
        // Create an Incoming Webhook connector in a Teams channel, or create a
        // Power Automate workflow (new-style) and paste the URL below.
        // Set type to 'legacy' for old connector cards, 'workflow' for the new
        // Power Automate / Adaptive Card format.
        'teams' => [
            'enabled'     => false,
            'webhook_url' => '',
            'type'        => 'legacy',   // 'legacy' or 'workflow'
        ],

        // ── Telegram ─────────────────────────────────────────────────────────
        // Create a bot via @BotFather and start a chat with it first.
        'telegram' => [
            'enabled'   => false,
            'bot_token' => '',
            'chat_id'   => '',
        ],

        // ── Slack ─────────────────────────────────────────────────────────────
        // Create an Incoming Webhook app at api.slack.com/apps.
        'slack' => [
            'enabled'     => false,
            'webhook_url' => '',
        ],

        // ── Discord ───────────────────────────────────────────────────────────
        // Channel Settings → Integrations → Webhooks → New Webhook.
        'discord' => [
            'enabled'     => false,
            'webhook_url' => '',
        ],

        // ── ntfy.sh ───────────────────────────────────────────────────────────
        // Use ntfy.sh (public) or self-hosted ntfy. Subscribe to the topic in
        // the ntfy mobile app or browser to receive notifications.
        'ntfy' => [
            'enabled' => false,
            'url'     => 'https://ntfy.sh',
            'topic'   => '',        // e.g. 'my-claude-alerts'
            // 'token' => '',       // Only needed for private/self-hosted topics
        ],

        // ── Email ─────────────────────────────────────────────────────────────
        // Uses PHP's built-in mail(). Make sure your hosting has a working MTA.
        // For SMTP, configure php.ini or use a transactional mail service.
        'email' => [
            'enabled'        => false,
            'to'             => '',
            'from'           => 'claude-notify@example.com',
            'subject_prefix' => '[Claude]',
        ],

    ],
];
