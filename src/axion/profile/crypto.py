"""Windows DPAPI protection without third-party dependencies."""
from __future__ import annotations
import base64, ctypes, os
from ctypes import wintypes

class DataBlob(ctypes.Structure):
    _fields_ = [("cbData", wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_char))]

class ProfileCrypto:
    available = os.name == "nt"
    def protect(self, value: str) -> str:
        if not self.available: raise RuntimeError("DPAPI encryption is unavailable; sensitive value was not stored.")
        raw = value.encode("utf-8"); source = DataBlob(len(raw), ctypes.cast(ctypes.create_string_buffer(raw), ctypes.POINTER(ctypes.c_char))); out = DataBlob()
        if not ctypes.windll.crypt32.CryptProtectData(ctypes.byref(source), None, None, None, None, 0, ctypes.byref(out)): raise ctypes.WinError()
        try: return base64.b64encode(ctypes.string_at(out.pbData, out.cbData)).decode("ascii")
        finally: ctypes.windll.kernel32.LocalFree(out.pbData)
    def unprotect(self, value: str) -> str:
        raw = base64.b64decode(value); source = DataBlob(len(raw), ctypes.cast(ctypes.create_string_buffer(raw), ctypes.POINTER(ctypes.c_char))); out = DataBlob()
        if not ctypes.windll.crypt32.CryptUnprotectData(ctypes.byref(source), None, None, None, None, 0, ctypes.byref(out)): raise ctypes.WinError()
        try: return ctypes.string_at(out.pbData, out.cbData).decode("utf-8")
        finally: ctypes.windll.kernel32.LocalFree(out.pbData)
