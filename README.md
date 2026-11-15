# Logic Pro Discord Presence

A personal, unofficial macOS integration that displays your Logic Pro session in Discord. Starts automatically at login, with no Dock or menu bar icon.

Inspired by [ReaCord](https://github.com/BartekStaniak/ReaCord). This is an external Swift/Python helper, not a native Logic plug-in and not a feature-complete port of ReaCord.

## Features

- Project name, filename, generic text, or hidden project information.
- Playing, Recording and Stopped states with status badges.
- Tempo and visible track count when exposed by Logic's Accessibility interface.
- Session timer: current project session, Logic session, or off.
- Incognito mode and a presence enable/disable switch.
- Local settings page with a snapshot of the last published presence.
- Automatic Discord reconnection and presence clearing when Logic closes.
- Uses local Discord IPC; no bot token or account credentials.

## Requirements

macOS, Logic Pro (including Creator Studio), Discord desktop, and Apple Command Line Tools (`xcode-select --install`) providing Swift and `/usr/bin/python3`. No third-party Python packages are required. Tested locally with macOS 26.6.2 and Logic Pro Creator Studio; other versions may expose different Accessibility controls.

## Install

```sh
git clone https://github.com/yuripa07/logic-pro-discord-presence.git
cd logic-pro-discord-presence
./install.sh
```

1. A shared Application ID is included. No Discord developer setup or bot token is needed. To use your own application instead, run `./configure.command`.
2. If using your own application, optionally configure its App Icon under General Information.
3. In macOS **System Settings → Privacy & Security → Accessibility**, add and enable `~/Library/Application Support/LogicDiscordPresence/logic-probe`. Use Command+Shift+G in the file picker to enter the path. Recompiling/updating the helper may require removing and re-adding its permission.
4. Open Discord and Logic, and enable activity sharing in Discord.

Installer preserves existing configuration. Running it on an existing installation recompiles the helper, restarts the service; the default Logic timer retains the actual process start time. No administrator privileges are needed.

You can also double-click `install.command` in the downloaded source folder. Apple Command Line Tools are still required to compile the helper.

## Settings

Run `./settings.command`. This opens a temporary local web interface on `127.0.0.1` with a random URL and request token. It stops after ten minutes; the background presence service continues independently. Reload to update its preview after applying settings. The preview is a snapshot, not an exact reproduction of Discord's UI.

## Behavior and limitations

- Samples Logic approximately every two seconds; sends changed presence and refreshes unchanged presence approximately every 30 seconds. Discord may delay visual updates independently.
- By default, the timer starts at the actual launch time of the Logic process and ends when Logic quits. Saving, switching windows/projects, reconnecting Discord and restarting this helper do not reset it. It is not active editing time. The optional project timer still follows observed project/window changes.
- Pause and Stop cannot reliably be distinguished; inactive playback is shown as Stopped.
- Track count reflects accessible track headers and may omit hidden, collapsed, filtered or virtualized tracks. It is labeled **visible tracks**.
- Missing permissions or unavailable controls result in generic text, not inferred recording/playback state.
- Project names are shared on your Discord profile unless hidden or incognito is enabled. The local status file also contains the most recently published payload.
- The service does not control Discord's recent-activity history or replace Discord's built-in detected-application catalog. Disabling built-in detection may affect history.
- The shared application uses Discord-hosted assets (logic, play, record, stop). Custom Application IDs fall back to public HTTPS artwork unless a custom logo is configured.
- No audio, keystrokes, project contents or recordings are captured. The helper only reads Accessibility attributes; it does not control transport.

## Troubleshooting

Inspect `~/Library/Application Support/LogicDiscordPresence/status.json` and `error.log`. `published` means Discord acknowledged the payload, not that its final rendering was visually verified. For missing project/transport information, check Accessibility. For missing presence, check your Application ID, Discord desktop and activity-sharing settings.

```sh
launchctl print gui/$(id -u)/local.logic-discord-presence
```

## Uninstall

```sh
./uninstall.sh
```

This stops the service and removes automatic startup. Your configuration and installed files remain in `~/Library/Application Support/LogicDiscordPresence`; you can delete that folder manually.

## Development

```sh
python3 -m unittest discover -s tests -v
```

`probe.swift` reads Logic state, `presence.py` implements IPC and presence formatting, and `settings.py` serves the optional configuration UI. Playback and recording were confirmed in a real local session; automated tests cover formatting, privacy and IPC framing rather than macOS UI or Discord rendering.

## Credits

Transport badge artwork is referenced from **ReaCord**, by BartekStaniak, under its MIT license; see `ReaCord-LICENSE.txt`. The Logic Pro icon belongs to Apple. The shared app uses artwork from Apple’s App Store; custom applications use Apple’s public support image. This project is not affiliated with Apple, Discord or ReaCord.
