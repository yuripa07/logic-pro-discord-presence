import http.server,json,secrets,webbrowser,threading
from pathlib import Path
from urllib.parse import parse_qs
BASE=Path(__file__).resolve().parent
TOKEN=secrets.token_urlsafe(24)
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args): pass
 def do_GET(self):
  if self.path!='/'+TOKEN: self.send_error(404); return
  cfg=json.loads((BASE/'config.json').read_text())
  html='''<!doctype html><meta charset="utf-8"><title>Logic Presence</title><style>body{background:#141416;color:#eee;font:16px system-ui;max-width:720px;margin:60px auto}section,form{background:#222226;border-radius:18px;padding:28px;margin:20px 0}label{display:block;margin:18px 0}select,input,button{font:inherit;padding:8px;border-radius:8px}button{background:#a697ff;border:0;padding:12px 24px}small{color:#bbb}img{width:80px;float:left;margin-right:20px}h1{margin-bottom:4px}</style><h1>Logic Presence</h1><small>Projeto, transporte e privacidade</small><section id="preview"></section><form method="post"><input type="hidden" name="token" value="TOKEN"><label>Nome do projeto <select name="project_mode"><option value="name">Nome</option><option value="filename">Nome do arquivo</option><option value="generic">Genérico</option><option value="hidden">Oculto</option></select></label><label>Temporizador <select name="timer"><option value="project">Sessão do projeto</option><option value="uptime">Sessão do Logic</option><option value="off">Desligado</option></select></label><label>Transporte <select name="transport"><option value="tempo">Estado e BPM quando disponíveis</option><option value="simple">Apenas estado</option><option value="hidden">Oculto</option></select></label><label><input type="checkbox" name="show_tracks"> Mostrar número de pistas quando detectável</label><label><input type="checkbox" name="incognito"> Incógnito (oculta projeto e pistas)</label><label><input type="checkbox" name="enabled"> Publicar presença</label><button>Aplicar</button></form><small>Não altera o áudio ou o projeto. Fechar esta página não desativa o serviço.</small><script>const cfg=CONFIG;for(const [k,v] of Object.entries(cfg)){const e=document.querySelector('[name="'+k+'"]');if(e){if(e.type==='checkbox')e.checked=v;else e.value=v}}const s=STATUS;const p=s.preview||{};const box=document.getElementById('preview');const img=document.createElement('img');img.src=(p.assets||{}).large_image||'';box.append(img);for(const t of ['Logic Pro',p.details,p.state,'Conexão: '+s.state]){const d=document.createElement('p');d.textContent=t||'';box.append(d)}</script>'''
  from presence import DEFAULTS
  status=json.loads((BASE/'status.json').read_text())
  html=html.replace('TOKEN',TOKEN).replace('CONFIG',json.dumps({**DEFAULTS,**cfg}).replace('<','\\u003c')).replace('STATUS',json.dumps(status).replace('<','\\u003c'))
  self.send_response(200);self.send_header('Content-Type','text/html; charset=utf-8');self.end_headers();self.wfile.write(html.encode())
 def do_POST(self):
  if self.path!='/'+TOKEN: self.send_error(404); return
  size=int(self.headers.get('Content-Length',0))
  if size>8192: self.send_error(413);return
  data=parse_qs(self.rfile.read(size).decode())
  if data.get('token')!=[TOKEN]:self.send_error(403);return
  cfg=json.loads((BASE/'config.json').read_text())
  for key,allowed in {'project_mode':['name','filename','generic','hidden'],'timer':['project','uptime','off'],'transport':['tempo','simple','hidden']}.items():
   value=data.get(key,[''])[0]
   if value not in allowed:self.send_error(400);return
   cfg[key]=value
  for key in ['show_tracks','incognito','enabled']:cfg[key]=key in data
  tmp=BASE/'config.tmp';tmp.write_text(json.dumps(cfg));tmp.replace(BASE/'config.json')
  self.send_response(303);self.send_header('Location','/'+TOKEN);self.end_headers()
s=http.server.HTTPServer(('127.0.0.1',0),Handler)
webbrowser.open('http://127.0.0.1:'+str(s.server_port)+'/'+TOKEN)
threading.Timer(600,s.shutdown).start()
s.serve_forever()
