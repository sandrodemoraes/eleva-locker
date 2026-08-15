#!/usr/bin/env python3
"""
Alinha tokens das ESPs no banco com os gravados no firmware (bancada).

As placas enviam token fixo no .ino; se o banco foi recriado, o token muda
e a API devolve 403 Token rejeitado.

Uso:
  py tools/corrigir_tokens_bancada.py
  py tools/corrigir_tokens_bancada.py --listar
"""
import argparse
import json
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository
from repositories.esp32_repository import Esp32Repository

# Tokens gravados no firmware (.ino) — atualize se regravar a placa
TOKENS_FIRMWARE = {
    "192.168.16.104": "2e5bb4db71d8330be8bae43b13ac19f6",  # Matriz ESP32-C3
    "192.168.16.121": "1bb2821a61346ed14c32664e62b18235",  # Bancada M1 (1-8)
    "192.168.16.145": "7c519983b4c875473452feed99b3d394",  # Bancada M2 (9-16)
    "192.168.16.146": "22bde9bb0745aa00731b292352c0b7b6",  # Bancada M3 (17-24)
}


def listar():
    with BaseRepository.get_connection() as conn:
        rows = conn.execute(
            "SELECT id, nome, ip, token FROM esp32 ORDER BY id"
        ).fetchall()
    print("\n  ESP no banco:")
    for r in rows:
        esperado = TOKENS_FIRMWARE.get(r["ip"], "—")
        ok = "OK" if r["token"] == esperado else "DIVERGE"
        print(f"    id={r['id']} | {r['nome']} | {r['ip']}")
        print(f"      banco:    {r['token']}")
        print(f"      firmware: {esperado} [{ok}]")
    return rows


def testar_token(url, token):
    req = urllib.request.Request(
        f"{url.rstrip('/')}/api/esp32/heartbeat?token={token}",
        data=json.dumps({"ip": "127.0.0.1", "sync_versao": 0}).encode(),
        headers={"Content-Type": "application/json", "X-ESP32-Token": token},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status
    except urllib.error.HTTPError as erro:
        return erro.code


def main():
    parser = argparse.ArgumentParser(description="Alinha tokens ESP bancada")
    parser.add_argument("--listar", action="store_true", help="Só listar tokens")
    parser.add_argument("--url", default="http://127.0.0.1:15000")
    args = parser.parse_args()

    print("=" * 60)
    print("  TOKENS ESP — BANCADA")
    print("=" * 60)

    rows = listar()
    if args.listar:
        return 0

    if not rows:
        print("\n  Nenhuma ESP cadastrada.")
        return 1

    corrigidos = 0
    for ip, token_fw in TOKENS_FIRMWARE.items():
        with BaseRepository.get_connection() as conn:
            esp = conn.execute(
                "SELECT * FROM esp32 WHERE ip = ? LIMIT 1", (ip,)
            ).fetchone()
        if not esp:
            print(f"\n  AVISO: nenhuma ESP com IP {ip}")
            continue
        if esp["token"] == token_fw:
            print(f"\n  {esp['nome']} ({ip}): token já OK")
            continue

        Esp32Repository.atualizar(esp["id"], {
            "nome": esp["nome"],
            "ip": esp["ip"],
            "mac": esp["mac"] or "",
            "armario": esp["armario"],
            "status": esp["status"],
            "token": token_fw,
            "porta": esp["porta"] or 80,
            "max_portas": esp["max_portas"] or 8,
        })
        print(f"\n  {esp['nome']} ({ip}): token atualizado")
        corrigidos += 1

    print(f"\n  Corrigidos: {corrigidos}")
    listar()

    print(f"\n  Testando API em {args.url} ...")
    for ip, token in TOKENS_FIRMWARE.items():
        code = testar_token(args.url, token)
        status = "OK" if code == 200 else f"HTTP {code}"
        print(f"    {ip}: {status}")

    print("\n" + "=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
