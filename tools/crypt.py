#!/usr/bin/env python3
"""Ver-/Entschlüsselt die Tracker-Daten.

  KT_PASS='…' python3 tools/crypt.py decrypt   # data.enc.json -> data.json (Klartext, gitignored)
  KT_PASS='…' python3 tools/crypt.py encrypt   # data.json -> data.enc.json

Format: AES-256-GCM, Schlüssel per PBKDF2-SHA256 (310 000 Iterationen). Kompatibel mit WebCrypto in index.html.
"""
import base64, json, os, sys
from pathlib import Path
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

ROOT = Path(__file__).resolve().parent.parent
ENC, PLAIN = ROOT / "data.enc.json", ROOT / "data.json"
ITER = 310_000
b64 = lambda b: base64.b64encode(b).decode()
unb64 = base64.b64decode

def key(pw, salt, it):
    return PBKDF2HMAC(hashes.SHA256(), 32, salt, it).derive(pw.encode())

def password():
    pw = os.environ.get("KT_PASS")
    if not pw:
        sys.exit("Fehler: Passwort fehlt (Umgebungsvariable KT_PASS setzen).")
    return pw

def decrypt():
    e = json.loads(ENC.read_text())
    try:
        pt = AESGCM(key(password(), unb64(e["salt"]), e["iter"])).decrypt(unb64(e["iv"]), unb64(e["ct"]), None)
    except Exception:
        sys.exit("Fehler: falsches Passwort oder beschädigte Datei.")
    PLAIN.write_text(json.dumps(json.loads(pt), ensure_ascii=False, indent=2) + "\n")
    print(f"entschlüsselt -> {PLAIN.name}")

def encrypt():
    data = json.loads(PLAIN.read_text())  # validiert JSON
    for k in ("ziele", "produkte", "eintraege"):
        assert k in data, f"Schlüssel '{k}' fehlt"
    salt, iv = os.urandom(16), os.urandom(12)
    ct = AESGCM(key(password(), salt, ITER)).encrypt(iv, json.dumps(data, ensure_ascii=False, separators=(",", ":")).encode(), None)
    ENC.write_text(json.dumps({"v": 1, "kdf": "PBKDF2-SHA256", "iter": ITER, "salt": b64(salt), "iv": b64(iv), "ct": b64(ct)}) + "\n")
    print(f"verschlüsselt -> {ENC.name} ({len(data['eintraege'])} Einträge)")

if __name__ == "__main__":
    {"decrypt": decrypt, "encrypt": encrypt}.get(sys.argv[1] if len(sys.argv) > 1 else "", lambda: sys.exit(__doc__))()
