#!/usr/bin/env python3
"""
Força o token da ESP oficial no banco e testa a API.

Uso:
  py tools/corrigir_token_esp.py
  py tools/corrigir_token_esp.py --token 2e5bb4db71d8330be8bae43b13ac19f6
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

from pathlib import Path
from repositories.esp32_repository import Esp32Repository

NOME_ESP = "ESP Matriz 8ch"
TOKEN_PADRAO = "2e5bb4db71d8330be8bae43b13ac19f6"


def testar_api(url_base, token):
    url_base = url_base.rstrip("/")
    req = urllib.request.Request(
        f"{url_base}/api/esp32/heartbeat?token={token}",
        data=json.dumps({"ip": "127.0.0.1", "sync_versao": 0}).encode(),
        headers={
            "Content-Type": "application/json",
            "X-ESP32-Token": token,
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as erro:
        return erro.code, erro.read().decode()


def main():
    parser = argparse.ArgumentParser(description="Corrige token ESP no banco")
    parser.add_argument("--token", default=TOKEN_PADRAO)
    parser.add_argument("--nome-esp", default=NOME_ESP)
    parser.add_argument("--url", default="http://127.0.0.1:15000")
    parser.add_argument("--sem-teste", action="store_true", help="Só grava no banco")
    args = parser.parse_args()

    token = args.token.strip()
    db_path = Path(__file__).resolve().parent.parent / "database" / "elevalocker.db"
    print(f"Banco: {db_path}")

    from repositories.base_repository import BaseRepository
    with BaseRepository.get_connection() as conn:
        esp = conn.execute(
            "SELECT * FROM esp32 WHERE nome = ? LIMIT 1",
            (args.nome_esp,),
        ).fetchone()

    if not esp:
        print(f"ESP '{args.nome_esp}' não encontrado. Rode: py tools/setup_oficial.py")
        return 1

    esp_id = esp["id"]
    print(f"ESP id={esp_id} | token antigo: {esp['token']!r}")

    Esp32Repository.atualizar(esp_id, {
        "nome": esp["nome"],
        "ip": esp["ip"],
        "mac": esp["mac"] or "",
        "armario": esp["armario"],
        "status": esp["status"],
        "token": token,
        "porta": esp["porta"] or 80,
        "max_portas": esp["max_portas"] or 8,
    })

    esp2 = Esp32Repository.buscar_por_token(token)
    print(f"Token gravado: {token}")
    print(f"Busca no banco: {'OK id=' + str(esp2['id']) if esp2 else 'FALHOU'}")

    if args.sem_teste:
        return 0 if esp2 else 1

    print(f"\nTestando API em {args.url} ...")
    print("(O servidor py app.py precisa estar RODANDO)")
    code, body = testar_api(args.url, token)
    print(f"HTTP {code}")
    print(body[:400])

    if code == 200:
        print("\n✅ Servidor aceitou o token. Reinicie a ESP ou aguarde sync.")
        return 0

    print("\n❌ Servidor ainda rejeita. Reinicie py app.py após git pull.")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
