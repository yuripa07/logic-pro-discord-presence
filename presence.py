#!/usr/bin/python3
import json, os, socket, struct, subprocess, time, uuid
from pathlib import Path
BASE = Path(__file__).resolve().parent

def send(s, op, obj):
    raw = json.dumps(obj).encode(); s.sendall(struct.pack('<II',op,len(raw))+raw)
def exact(s,n):
    buf=b''
    while len(buf)<n:
        chunk=s.recv(n-len(buf))
        if not chunk: raise ConnectionError('IPC closed')
        buf+=chunk
    return buf
def receive(s):
    while True:
        op,n=struct.unpack('<II',exact(s,8))
        if n>1048576: raise ValueError('IPC frame too large')
        raw=exact(s,n); obj=json.loads(raw)
        if op==3: send(s,4,obj); continue
        if op==2: raise ConnectionError('Discord closed connection')
        return obj
def connect(appid):
    roots=[os.environ.get('TMPDIR',''),'/tmp',str(Path.home()/'Library/Application Support/discord')]
    for root in filter(None,roots):
        for i in range(10):
            s=socket.socket(socket.AF_UNIX); s.settimeout(3)
            try:
                s.connect(str(Path(root)/('discord-ipc-'+str(i))))
                send(s,0,{'v':1,'client_id':appid})
                if receive(s).get('evt')!='READY': raise ConnectionError('Handshake rejected')
                return s
            except (OSError,ValueError,ConnectionError): s.close()
    raise ConnectionError('Discord IPC unavailable or application ID rejected')
DEFAULTS = {'project_mode':'name','timer':'project','transport':'tempo','incognito':False,'show_tracks':True,'enabled':True,'logo':'https://cdsassets.apple.com/live/7WUAS350/images/pro-apps/creator-studio-logic-pro-12-4-app-icon.png'}
def activity(probe,start,cfg=None):
    cfg={**DEFAULTS,**(cfg or {})}
    if not probe.get('running') or not cfg['enabled']: return None
    inc=cfg['incognito']; mode=cfg['project_mode']
    result={'assets':{'large_image':cfg['logo'],'large_text':'Logic Pro'}}
    project=probe.get('project','Working on a project')
    if inc or mode=='generic': result['details']='Working on a project'
    elif mode!='hidden': result['details']=(probe.get('filename',project) if mode=='filename' else project)[:120]
    state=probe.get('transport','Producing music')
    if inc: state='Incognito'
    elif cfg['transport']=='hidden': state=''
    elif cfg['transport']=='tempo' and probe.get('bpm'): state+=' · '+str(probe['bpm'])+' BPM'
    if not inc and cfg['show_tracks'] and probe.get('tracks') is not None: state+=(' · ' if state else '')+str(probe['tracks'])+(' visible track' if probe['tracks']==1 else ' visible tracks')
    if state: result['state']=state[:120]
    if cfg['timer']!='off' and start: result['timestamps']={'start':start}
    badge={'Playing':'play','Recording':'record','Paused':'pause','Stopped':'stop'}.get(probe.get('transport'))
    if badge and not inc and cfg['transport']!='hidden':
        result['assets'].update(small_image='https://raw.githubusercontent.com/BartekStaniak/ReaCord/main/assets/discord/'+badge+'.png',small_text=probe['transport'])
    return result
def run():
    s=None; client=None; session=None; started=None; uptime=None; last_payload=None; last_sent=0
    while True:
        status={}
        try:
            cfg=json.loads((BASE/'config.json').read_text()); appid=str(cfg.get('application_id','')).strip()
            cfg={**DEFAULTS,**cfg}
            p=json.loads(subprocess.check_output([str(BASE/'logic-probe')],timeout=8))
            if p.get('running') and uptime is None: uptime=int(time.time())
            if not p.get('running'): uptime=None
            key=(p.get('pid'),p.get('project')) if p.get('running') else None
            if key!=session: session=key; started=int(time.time()) if key else None
            status={'logic_running':p.get('running'),'accessibility':p.get('accessible'),'application_id_configured':bool(appid),'updated':int(time.time())}
            if appid!=client:
                if s: s.close()
                s=None; client=appid; last_payload=None
            if not appid: status['state']='waiting_for_application_id'
            elif not appid.isdigit() or not 17<=len(appid)<=22: status['state']='invalid_application_id'
            else:
                if s is None: s=connect(appid); last_payload=None
                payload=activity(p,uptime if cfg['timer']=='uptime' else started,cfg)
                if payload==last_payload and time.time()-last_sent<30:
                    time.sleep(2); continue
                nonce=str(uuid.uuid4()); send(s,1,{'cmd':'SET_ACTIVITY','args':{'pid':os.getpid(),'activity':payload},'nonce':nonce})
                for _ in range(20):
                    reply=receive(s)
                    if reply.get('nonce')==nonce:
                        if reply.get('evt')=='ERROR': raise RuntimeError('Discord rejected activity: '+str(reply.get('data',{})))
                        break
                else: raise RuntimeError('Missing Discord acknowledgement')
                last_payload=payload; last_sent=time.time()
                status['state']='published' if payload else 'idle'
                status['preview']=payload
        except Exception as e:
            status['state']='retrying'; status['error']=str(e)
            if s: s.close()
            s=None
        tmp=BASE/'status.tmp'; tmp.write_text(json.dumps(status,indent=2)); tmp.replace(BASE/'status.json')
        time.sleep(2)
if __name__=='__main__': run()
