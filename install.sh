#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
[[ "$(uname -s)" == Darwin ]] || { echo 'Requires macOS'; exit 1; }
base="$HOME/Library/Application Support/LogicDiscordPresence"
mkdir -p "$base" "$HOME/Library/LaunchAgents"
build_dir=$(mktemp -d)
trap 'rm -rf "$build_dir"' EXIT
xcrun swiftc probe.swift -o "$build_dir/logic-probe"
# Compile before touching an existing installation.
cp "$build_dir/logic-probe" "$base/logic-probe"
cp presence.py settings.py "$base/"
/usr/bin/python3 - "$base" <<'PY'
import json,sys,pathlib,plistlib,os,subprocess
base=pathlib.Path(sys.argv[1])
config=base/'config.json'
if not config.exists(): config.write_text(json.dumps({'application_id':''})+'\n')
agent=pathlib.Path.home()/'Library/LaunchAgents/local.logic-discord-presence.plist'
data={'Label':'local.logic-discord-presence','ProgramArguments':['/usr/bin/python3',str(base/'presence.py')],'RunAtLoad':True,'KeepAlive':True,'ThrottleInterval':30,'ProcessType':'Background','StandardOutPath':str(base/'service.log'),'StandardErrorPath':str(base/'error.log')}
agent.write_bytes(plistlib.dumps(data))
domain='gui/'+str(os.getuid())
subprocess.run(['launchctl','bootout',domain,str(agent)],capture_output=True)
subprocess.run(['launchctl','bootstrap',domain,str(agent)],check=True)
PY
printf 'Installed. Run ./configure.command to set your Discord Application ID.\nAuthorize logic-probe in System Settings > Privacy & Security > Accessibility.\n'
