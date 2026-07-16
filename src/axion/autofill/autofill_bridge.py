"""Token-authenticated localhost HTTP bridge."""
from __future__ import annotations
import json, secrets, threading, time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse
from axion.profile.profile_vault import ProfileVault, SENSITIVE
from axion.autofill.field_mapper import document_label
from axion.tools.smart_file_finder import SmartFileFinder

class AutofillBridge:
    host="127.0.0.1"
    def __init__(self,vault=None,settings_path=None,port=8765,finder=None):
        self.vault=vault or ProfileVault(); self.finder=finder or SmartFileFinder(); self.settings_path=settings_path or Path("data/autofill/autofill_settings.json"); self.port=port; self.token=None; self.server=None; self.thread=None; self._approval=False
    @property
    def running(self): return bool(self.thread and self.thread.is_alive())
    def start(self):
        if self.running:return "Autofill bridge is already running."
        self.token=secrets.token_urlsafe(32); bridge=self
        class Handler(BaseHTTPRequestHandler):
            def do_OPTIONS(self): self.send_response(204); self._headers(); self.end_headers()
            def do_POST(self):
                try:
                    size=int(self.headers.get("Content-Length","0")); payload=json.loads(self.rfile.read(min(size,65536)) or b"{}")
                    if self.headers.get("X-Axion-Token")!=bridge.token:return self._json(403,{"error":"invalid token"})
                    if self.path not in {"/v1/fields","/v1/document"}:return self._json(404,{"error":"not found"})
                    if self.path=="/v1/document":
                        domain=str(payload.get("domain","")).lower()
                        if not bridge.site_allowed(domain):return self._json(403,{"error":"site not allowed"})
                        label=document_label(str(payload.get("label","")))
                        files=bridge.vault.files(); path=files.get(label or ""); alternatives=[]
                        if not path and label:
                            try: alternatives=[{"filename":x.filename,"path":x.path,"reason":x.reason} for x in bridge.finder.search(label,"documents")[:5]]
                            except (OSError,ValueError): alternatives=[]
                        suggestion={"filename":Path(path).name,"path":path,"reason":f"registered profile file: {label}"} if path else (alternatives[0] if alternatives else None)
                        return self._json(200,{"label":label,"suggestion":suggestion,"alternatives":alternatives[1:] if suggestion and alternatives else alternatives})
                    domain=str(payload.get("domain","")).lower(); fields=payload.get("fields",[])
                    if not isinstance(fields,list) or len(fields)>50 or not all(isinstance(x,str) for x in fields):return self._json(400,{"error":"invalid fields"})
                    if not bridge.site_allowed(domain):return self._json(403,{"error":"site not allowed"})
                    sensitive=any(x in SENSITIVE for x in fields)
                    if sensitive and not bridge.consume_sensitive():return self._json(403,{"error":"sensitive approval required"})
                    return self._json(200,{"fields":bridge.vault.requested(fields)})
                except (ValueError,TypeError):return self._json(400,{"error":"invalid request"})
            def _headers(self): self.send_header("Content-Type","application/json"); self.send_header("Access-Control-Allow-Origin","chrome-extension://*"); self.send_header("Access-Control-Allow-Headers","Content-Type, X-Axion-Token")
            def _json(self,code,data): self.send_response(code); self._headers(); self.end_headers(); self.wfile.write(json.dumps(data).encode())
            def log_message(self,format,*args): pass
        self.server=ThreadingHTTPServer((self.host,self.port),Handler); self.port=self.server.server_address[1]; self.thread=threading.Thread(target=self.server.serve_forever,daemon=True); self.thread.start(); return f"Autofill bridge running on {self.host}:{self.port}. Session token: {self.token}"
    def stop(self):
        if self.server:self.server.shutdown(); self.server.server_close()
        self.server=None; self.thread=None; self.token=None; self._approval=False; return "Autofill bridge stopped."
    def approve_sensitive(self): self._approval=True
    def consume_sensitive(self): approved=self._approval; self._approval=False; return approved
    def revoke_sensitive(self): self._approval=False
    def settings(self):
        try:return json.loads(self.settings_path.read_text(encoding="utf-8"))
        except (OSError,ValueError):return {"allowed_sites":[],"blocked_sites":[]}
    def update_site(self,domain,allow):
        domain=urlparse("//"+domain.strip(),scheme="https").hostname
        if not domain:raise ValueError("Invalid domain.")
        data=self.settings(); target="allowed_sites" if allow else "blocked_sites"; other="blocked_sites" if allow else "allowed_sites"; data[target]=sorted(set(data[target]+[domain])); data[other]=[x for x in data[other] if x!=domain]; self.settings_path.parent.mkdir(parents=True,exist_ok=True); self.settings_path.write_text(json.dumps(data,indent=2),encoding="utf-8")
    def site_allowed(self,domain):
        data=self.settings(); domain=domain.lower().split(":")[0]
        if domain in data["blocked_sites"]:return False
        return domain in data["allowed_sites"]
