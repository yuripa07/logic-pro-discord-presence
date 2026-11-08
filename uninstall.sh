#!/bin/bash
set -euo pipefail
agent="$HOME/Library/LaunchAgents/local.logic-discord-presence.plist"
launchctl bootout "gui/$(id -u)" "$agent" 2>/dev/null || true
rm -f "$agent"
echo 'Service stopped and login startup removed. Configuration and files retained in ~/Library/Application Support/LogicDiscordPresence.'
