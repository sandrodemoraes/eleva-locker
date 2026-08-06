#!/usr/bin/env python3
"""
Testa token ESP32 contra a API (mesmo fluxo da placa).

Uso:
  py tools/testar_token_esp.py
  py tools/testar_token_esp.py --token 2e5bb4db71d8330be8bae43b13ac19f6
  py tools/testar_token_esp.py --url http://192.168.16.130:15000
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.esp32_repository import Esp32Repository


def obter_token_padrao():
    from pathlib import Path
    db_path = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"
    print(f"Banco SQLite: {db_path}")

    esps = Esp32Repository.listar()
    if not esps:
        print("Nenhum ESP cadastrado.")
        return None
    esp = esps[0]
    print(f"ESP: id={esp['id']} nome={esp['nome']} token={esp['token']}")
    return esp["token"]


def testar(url_base, token):
    url_base = url_base.rstrip("/")
    headers = {
        "Content-Type": "application/json",
        "X-ESP32-Token": token,
    }

    print("\n--- POST /api/esp32/heartbeat ---")
    req = urllib.request.Request(
        f"{url_base}/api/esp32/heartbeat?token={token}",
        data=json.dumps({"ip": "127.0.0.1", "sync_versao": 0}).encode(),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode()
            print(f"HTTP {resp.status} OK")
            print(body[:300])
    except urllib.error.HTTPError as erro:
        print(f"HTTP {erro.code} — {erro.read().decode()[:300]}")
        return False

    print("\n--- GET /api/esp32/sync ---")
    req = urllib.request.Request(
        f"{url_base}/api/esp32/sync?token={token}",
        headers={"X-ESP32-Token": token},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            body = resp.read().decode()
            print(f"HTTP {resp.status} OK")
            data = json.loads(body)
            sync = data.get("sync", {})
            print(f"sync versao={sync.get('versao')} max_portas={sync.get('max_portas')}")
    except urllib.error.HTTPError as erro:
        print(f"HTTP {erro.code} — {erro.read().decode()[:300]}")
        return False

    return True


def main():
    parser = argparse.ArgumentParser(description="Testa token ESP32 na API")
    parser.add_argument("--token", help="Token (default: primeiro ESP do banco)")
    parser.add_argument("--url", default="http://127.0.0.1:15000", help="URL do servidor")
    args = parser.parse_args()

    token = args.token or obter_token_padrao()
    if not token:
        return 1

    token = token.strip()
    print(f"\nToken ({len(token)} chars): {token}")

    ok = testar(args.url, token)
    print("\n" + ("✅ API aceitou o token" if ok else "❌ API rejeitou — veja HTTP acima"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
