#!/bin/bash
set -euo pipefail
read -r -p 'Discord Application ID: ' appid
/usr/bin/python3 - "$appid" <<'PY'
import json,sys,pathlib
value=sys.argv[1].strip()
if not value.isdigit() or not 17<=len(value)<=22: raise SystemExit('Invalid Application ID (not a bot token).')
p=pathlib.Path.home()/'Library/Application Support/LogicDiscordPresence/config.json'
c=json.loads(p.read_text());c['application_id']=value
q=p.with_suffix('.tmp');q.write_text(json.dumps(c)+'\n');q.replace(p)
print('Saved. The running service picks up this change automatically.')
PY
