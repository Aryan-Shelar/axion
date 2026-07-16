"""Validated, encrypted-at-rest local profile storage."""
from __future__ import annotations
import json, re
from pathlib import Path
from .crypto import ProfileCrypto

FIELDS = {"full_name","first_name","middle_name","last_name","email","alternate_email","phone","alternate_phone","date_of_birth","gender","address_line1","address_line2","city","state","postal_code","country","college","course","year","github","linkedin","portfolio","aadhaar","pan"}
SENSITIVE = {"phone","alternate_phone","date_of_birth","address_line1","address_line2","postal_code","aadhaar","pan"}
class ProfileVault:
    def __init__(self, path: Path | None = None, crypto: ProfileCrypto | None = None): self.path=path or Path("data/profile/profile_vault.json"); self.crypto=crypto or ProfileCrypto()
    def create(self): self._save({"fields":{},"files":{}})
    def configured(self): return bool(self._load()["fields"] or self._load()["files"])
    def set(self, field: str, value: str):
        if field not in FIELDS: raise ValueError("Unsupported profile field.")
        self._validate(field,value); data=self._load(); data["fields"][field]={"encrypted":field in SENSITIVE,"value":self.crypto.protect(value) if field in SENSITIVE else value}; self._save(data)
    def get(self, field: str):
        item=self._load()["fields"].get(field)
        if not item:return None
        return self.crypto.unprotect(item["value"]) if item.get("encrypted") else item["value"]
    def remove(self, field): data=self._load(); data["fields"].pop(field,None); self._save(data)
    def add_file(self,label,path):
        file=Path(path).expanduser()
        if not file.is_file(): raise ValueError("Profile file does not exist.")
        data=self._load(); data["files"][label.lower().strip()]=str(file.resolve()); self._save(data)
    def remove_file(self,label): data=self._load(); data["files"].pop(label.lower().strip(),None); self._save(data)
    def files(self): return dict(self._load()["files"])
    def requested(self, fields): return {f:self.get(f) for f in fields if f in FIELDS and self.get(f) is not None}
    def show(self):
        values=[]
        for field in sorted(self._load()["fields"]): values.append(f"{field}: {mask_value(field,self.get(field) or '')}")
        return "\n".join(values) if values else "Profile vault is empty."
    def _validate(self,field,value):
        if not value.strip(): raise ValueError("Profile value cannot be empty.")
        if "email" in field and not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+",value): raise ValueError("Invalid email address.")
        if field=="aadhaar" and not re.fullmatch(r"\d{12}",re.sub(r"\s","",value)): raise ValueError("Aadhaar must contain 12 digits.")
        if field=="pan" and not re.fullmatch(r"[A-Z]{5}\d{4}[A-Z]",value.upper()): raise ValueError("Invalid PAN format.")
    def _load(self):
        try: data=json.loads(self.path.read_text(encoding="utf-8")); return {"fields":data.get("fields",{}),"files":data.get("files",{})}
        except (OSError,ValueError): return {"fields":{},"files":{}}
    def _save(self,data): self.path.parent.mkdir(parents=True,exist_ok=True); self.path.write_text(json.dumps(data,indent=2),encoding="utf-8")
def mask_value(field,value):
    if field in {"phone","alternate_phone","aadhaar"}: return "*"*max(0,len(value)-4)+value[-4:]
    if field=="pan" and len(value)>=10:return value[:2]+"***"+value[5:9]+"*"
    if field in SENSITIVE:return "********"
    return value
