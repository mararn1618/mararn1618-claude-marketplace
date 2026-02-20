<?php
declare(strict_types=1);

header('Content-Type: application/json');

// ── Config ───────────────────────────────────────────────────────────────────

$configFile = __DIR__ . '/config.php';
if (!file_exists($configFile)) {
    http_response_code(500);
    echo json_encode(['success' => false, 'error' => 'config.php not found — copy config.example.php to config.php and fill in your values']);
    exit;
}
$config = require $configFile;

// ── Auth ─────────────────────────────────────────────────────────────────────

$apiKey = $_SERVER['HTTP_X_API_KEY'] ?? '';
if (!hash_equals($config['api_key'], $apiKey)) {
    http_response_code(401);
    echo json_encode(['success' => false, 'error' => 'Unauthorized']);
    exit;
}

// ── Routing ──────────────────────────────────────────────────────────────────

$method = $_SERVER['REQUEST_METHOD'];
$action = $_GET['action'] ?? '';

if ($method === 'GET' && $action === 'channels') {
    listChannels($config);
} elseif ($method === 'POST') {
    sendNotification($config);
} else {
    http_response_code(405);
    echo json_encode(['success' => false, 'error' => 'Method not allowed']);
}

// ── Handlers ─────────────────────────────────────────────────────────────────

function listChannels(array $config): void
{
    $enabled = array_keys(array_filter(
        $config['channels'],
        static fn(array $c): bool => (bool)($c['enabled'] ?? false)
    ));
    echo json_encode(['channels' => array_values($enabled)]);
}

function sendNotification(array $config): void
{
    $body = json_decode(file_get_contents('php://input'), true) ?? [];
    $message     = trim($body['message'] ?? '');
    $channelName = $body['channel'] ?? null;

    if ($message === '') {
        http_response_code(400);
        echo json_encode(['success' => false, 'error' => '"message" is required']);
        return;
    }

    $targets = $channelName !== null
        ? [$channelName]
        : array_keys(array_filter($config['channels'], static fn(array $c): bool => (bool)($c['enabled'] ?? false)));

    $sent   = [];
    $errors = [];

    foreach ($targets as $name) {
        $channelConfig = $config['channels'][$name] ?? null;

        if ($channelConfig === null || !($channelConfig['enabled'] ?? false)) {
            $errors[$name] = 'Channel not found or disabled';
            continue;
        }

        try {
            switch ($name) {
                case 'teams':    sendTeams($channelConfig, $message);    break;
                case 'telegram': sendTelegram($channelConfig, $message); break;
                case 'slack':    sendSlack($channelConfig, $message);    break;
                case 'discord':  sendDiscord($channelConfig, $message);  break;
                case 'ntfy':     sendNtfy($channelConfig, $message);     break;
                case 'email':    sendEmail($channelConfig, $message);    break;
                default:         throw new RuntimeException("Unknown channel: $name");
            }
            $sent[] = $name;
        } catch (RuntimeException $e) {
            $errors[$name] = $e->getMessage();
        }
    }

    $success  = !empty($sent);
    $response = ['success' => $success, 'sent' => $sent];
    if (!empty($errors)) {
        $response['errors'] = $errors;
    }

    http_response_code($success ? 200 : 500);
    echo json_encode($response);
}

// ── HTTP helper ──────────────────────────────────────────────────────────────

function httpPost(string $url, string $payload, array $headers = []): string
{
    $ctx = stream_context_create([
        'http' => [
            'method'        => 'POST',
            'header'        => implode("\r\n", $headers),
            'content'       => $payload,
            'timeout'       => 15,
            'ignore_errors' => true,
        ],
        'ssl' => ['verify_peer' => true],
    ]);

    $result = @file_get_contents($url, false, $ctx);
    if ($result === false) {
        throw new RuntimeException("HTTP POST failed to: $url");
    }
    return $result;
}

// ── Channel senders ───────────────────────────────────────────────────────────

function sendTeams(array $cfg, string $message): void
{
    $type = $cfg['type'] ?? 'legacy';

    if ($type === 'workflow') {
        // Power Automate / new-style Teams webhook (Adaptive Card)
        $payload = json_encode([
            'type'        => 'message',
            'attachments' => [[
                'contentType' => 'application/vnd.microsoft.card.adaptive',
                'content'     => [
                    '$schema' => 'http://adaptivecards.io/schemas/adaptive-card.json',
                    'type'    => 'AdaptiveCard',
                    'version' => '1.2',
                    'body'    => [[
                        'type' => 'TextBlock',
                        'text' => $message,
                        'wrap' => true,
                    ]],
                ],
            ]],
        ]);
    } else {
        // Legacy Incoming Webhook connector (MessageCard)
        $payload = json_encode([
            '@type'      => 'MessageCard',
            '@context'   => 'http://schema.org/extensions',
            'themeColor' => '0076D7',
            'summary'    => 'Claude Notification',
            'sections'   => [[
                'text' => nl2br(htmlspecialchars($message, ENT_QUOTES, 'UTF-8')),
            ]],
        ]);
    }

    httpPost($cfg['webhook_url'], $payload, ['Content-Type: application/json']);
}

function sendTelegram(array $cfg, string $message): void
{
    $url     = "https://api.telegram.org/bot{$cfg['bot_token']}/sendMessage";
    $payload = json_encode([
        'chat_id'    => $cfg['chat_id'],
        'text'       => $message,
        'parse_mode' => 'HTML',
    ]);

    $response = httpPost($url, $payload, ['Content-Type: application/json']);
    $data     = json_decode($response, true);
    if (!($data['ok'] ?? false)) {
        throw new RuntimeException($data['description'] ?? 'Telegram send failed');
    }
}

function sendSlack(array $cfg, string $message): void
{
    $payload = json_encode(['text' => $message]);
    httpPost($cfg['webhook_url'], $payload, ['Content-Type: application/json']);
}

function sendDiscord(array $cfg, string $message): void
{
    $payload = json_encode(['content' => $message]);
    httpPost($cfg['webhook_url'], $payload, ['Content-Type: application/json']);
}

function sendNtfy(array $cfg, string $message): void
{
    $url     = rtrim($cfg['url'] ?? 'https://ntfy.sh', '/') . '/' . $cfg['topic'];
    $headers = ['Content-Type: text/plain; charset=utf-8'];
    if (!empty($cfg['token'])) {
        $headers[] = 'Authorization: Bearer ' . $cfg['token'];
    }
    httpPost($url, $message, $headers);
}

function sendEmail(array $cfg, string $message): void
{
    $subject = ($cfg['subject_prefix'] ?? '[Claude]') . ' ' . mb_substr($message, 0, 60);
    $headers = 'From: ' . ($cfg['from'] ?? 'noreply@example.com') . "\r\n" .
               'Content-Type: text/plain; charset=utf-8';

    if (!mail($cfg['to'], $subject, $message, $headers)) {
        throw new RuntimeException('mail() returned false — check server MTA config');
    }
}
