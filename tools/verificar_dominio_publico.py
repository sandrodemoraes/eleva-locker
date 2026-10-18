"""Checklist rápido pós-configuração de domínio público."""
import os
import socket
import sys
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

import config  # noqa: E402


def _ok(msg):
    print(f"  OK   {msg}")


def _falha(msg):
    print(f"  FALHA {msg}")


def main():
    base = (config.APP_URL_BASE or "").strip().rstrip("/")
    print()
    print("=" * 60)
    print("  VERIFICAR DOMÍNIO PÚBLICO — ELEVA LOCKER")
    print("=" * 60)
    print(f"  APP_URL_BASE = {base!r}")
    print()

    if not base:
        _falha("APP_URL_BASE vazio no .env")
        return 1

    if base.startswith("http://192.168.") or base.startswith("http://10."):
        _falha("Ainda usando IP local — atualize .env após configurar domínio")
        return 1

    if not base.startswith("https://"):
        _falha("Use HTTPS no APP_URL_BASE (https://seu-dominio...)")
        return 1

    host = base.replace("https://", "").replace("http://", "").split("/")[0]
    try:
        ip = socket.gethostbyname(host)
        _ok(f"DNS {host} → {ip}")
    except socket.gaierror as erro:
        _falha(f"DNS não resolve {host}: {erro}")
        return 1

    for path in ("/", "/totem/2", "/dashboard"):
        url = f"{base}{path}"
        try:
            req = urllib.request.Request(url, method="GET")
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status < 500:
                    _ok(f"HTTP {resp.status} {url}")
                else:
                    _falha(f"HTTP {resp.status} {url}")
        except urllib.error.HTTPError as erro:
            if erro.code in (200, 301, 302, 401, 403):
                _ok(f"HTTP {erro.code} {url}")
            else:
                _falha(f"HTTP {erro.code} {url}")
        except Exception as erro:
            _falha(f"{url} — {erro}")

    print()
    print("  Se tudo OK pelo 4G, atualize NOTIF_INCLUIR_LINK_TOTEM=1 no .env")
    print("=" * 60)
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
