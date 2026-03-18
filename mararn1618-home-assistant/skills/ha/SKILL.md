---
description: "Personal Home Assistant setup profile — connection details, room layout, devices, integrations, guardrails, and session workflow for Markus' local HA instance"
---

# Markus' Home Assistant Setup Profile

This skill provides context about a specific Home Assistant instance. Use it alongside the generic `home-assistant-manager` skill which covers workflows, patterns, and pitfalls.

## Connection Details

- **HA URL**: http://homeassistant.local:8123
- **SSH**: `root@homeassistant.local`
- **hass-cli**: Requires `source .env` (sets HASS_SERVER + HASS_TOKEN)
- **Browser**: claude-in-chrome for UI checks and dashboard previews

## System

- **OS**: HAOS 17.0
- **HA Core**: 2026.3.1
- **Machine**: qemux86-64 (VM, amd64)
- **Timezone**: Europe/Berlin
- **Entities**: ~992 total (306 sensor, 112 automation, 94 update, 92 switch, 71 binary_sensor, 33 light, 16 media_player, 5 cover, 1 climate)

## Zigbee Setup

- **Integration**: ZHA (NOT deCONZ — deCONZ is installed as add-on but ZHA is the active Zigbee integration)
- **Coordinator**: bellows/EZSP-based (Sonoff)
- **Coordinator Location**: Arbeitszimmer (AZ), 2nd floor
- **ZHA Toolkit**: Installed (tuya_magic, scan_device, etc.)
- **Device Manufacturers**: Nous/Tuya (TS011F Plugs, `a4:c1:38:*` IEEE prefix), Philips Hue, Aqara, Sonoff

## Rooms & Key Devices

| Room | Key | Devices |
|------|-----|---------|
| Wohnzimmer | WZ | Aqara Cube, Philips Dial Switch, Scenes, Sofa-Presence, Fische, Gaming Laptop |
| Arbeitszimmer | AZ | Tap Dial Switch, Markise, AC (Klimaanlage), Ventilator, Zigbee Coordinator |
| Kueche | - | Espressomaschine (auto-on morgens), Kuechenzeile-Licht, Fenster-Licht |
| Badezimmer | BZ | Button Licht/Lueftung, Humidity-basierter Luefter, Auto-off Timer |
| Schlafzimmer | SZ | Markise, Warnung bei offenen Fenstern/Tueren |
| Gaestezimmer | GZ | Rollos (Sonoff Button), Licht |
| Wintergarten | WG | Markise, Pumpe, Kleines Licht, Fische |
| Keller | - | Bewegungslicht, Wassersensor (Hebeanlage), Alarm bei Naesse |
| Flur 0/1 | - | Bewegungslicht nach Tageszeit |
| Garten/Vorgarten | - | Gartenlicht (Sunset-basiert), Flutlicht, Briefkasten-Sensor |

## Key Integrations

- **ZHA**: Active Zigbee integration (bellows/EZSP)
- **deCONZ**: Add-on installed but NOT active for Zigbee
- **Meross**: Smart Switches/Plugs (local broker add-on)
- **Philips Hue**: Tap Dial Switches (AZ, WZ)
- **Sonoff**: Buttons (GZ Rollos)
- **Alexa**: Media Player, Volume-Reset automation
- **Spotify**: Integration (used by Panic Button)
- **HACS**: Installed
- **DuckDNS + NGINX SSL Proxy**: External access
- **Google Drive Backup**: Automatic backups

## Add-ons

Terminal & SSH, Advanced SSH & Web Terminal, File Editor, Studio Code Server, deCONZ, DuckDNS, FTP, NGINX SSL Proxy, Meross Local Broker, Google Drive Backup

## Notable Automations & Features

- **Espressomaschine**: Auto-on mornings triggered by phone charging status
- **Aqara Cube**: Wohnzimmer control (rotate, shake = scenes)
- **Panic Button**: Custom events, scene cycling, Spotify integration
- **TEMPEH Maker**: Fermentation monitoring automations
- **Fische fuettern**: Feeding tracker with counter and reminder
- **Markisen**: Auto-retract on strong wind
- **Alexa Volume Reset**: Automated volume normalization

## Guardrails — CRITICAL SAFETY RULES

### NEVER without explicit user confirmation:
- `ha core restart` or `ha host reboot`
- `ha core update` or version upgrades
- Deleting automations, scripts, scenes, or entities
- Modifying `configuration.yaml` core settings
- Anything in `.storage/` that affects registries
- `rm` commands on the HA instance
- Changing network/DNS/hostname settings
- Disabling or removing integrations/add-ons

### ALWAYS before making changes:
1. **Read first** — understand current state before modifying
2. **Backup** — copy the file being changed into the project repo before editing on HA
3. **Validate** — run `ssh root@homeassistant.local "ha core check"` before any restart
4. **Prefer reload over restart**
5. **Log the session** — update `diary.md`

### Safe operations (no confirmation needed):
- Reading states, logs, config checks
- Listing entities, automations, integrations
- Browsing the HA UI
- Reloading automations/scripts/scenes

## Session Workflow

1. Read `diary.md` and relevant `knowledge/` files for context
2. Diagnose the issue (read states, logs, configs)
3. Propose a fix and get user confirmation
4. Implement (scp for iteration, git for final)
5. Verify (check logs, test trigger, confirm state)
6. Update `diary.md` with session summary
7. Update `knowledge/` files if something new was learned

## Project Path

`/Users/work1618/claude_projects/claude_code_homeassistant`

## Language

The user communicates in German. Responses should be in German. Technical terms (entity names, YAML keys, commands) stay in English.
