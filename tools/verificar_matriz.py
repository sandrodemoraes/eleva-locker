#!/usr/bin/env python3
"""
Verifica se a instalação Matriz está correta (antes/depois de atualizar).

Checa: .env, banco SQLite vs Postgres, armário id 3, ESP único, firmware.

Uso:
  python tools/verificar_matriz.py
  python tools/verificar_matriz.py --token 2e5bb4db...
  python tools/verificar_matriz.py --strict   # exit 1 se houver problema
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

import config  # noqa: E402
from database import criar_banco  # noqa: E402

criar_banco()

from repositories.base_repository import BaseRepository  # noqa: E402

NOME_ARMARIO = "ELEVA Locker Matriz"
NOME_ESP = "ESP Matriz 8ch"
ARMARIO_ID_ESPERADO = "3"
FIRMWARE_DST = ROOT / "firmware" / "elevalocker_sync" / "elevalocker_sync.ino"
FIRMWARE_SRC = ROOT / "firmware" / "elevalocker_sync.ino"

problemas = []
avisos = []


def ok(msg):
    print(f"  OK  {msg}")


def aviso(msg):
    avisos.append(msg)
    print(f"  !!  {msg}")


def erro(msg):
    problemas.append(msg)
    print(f"  XX  {msg}")


def verificar_env(token_esperado):
    print("\n--- .env ---")
    env_path = ROOT / ".env"
    if not env_path.exists():
        erro(".env não encontrado — copie de .env.example")
        return

    ok(f".env existe ({env_path})")

    totem_id = (config.TOTEM_ARMARIO_ID or "").strip()
    if totem_id == ARMARIO_ID_ESPERADO:
        ok(f"TOTEM_ARMARIO_ID={totem_id}")
    elif not totem_id:
        erro("TOTEM_ARMARIO_ID vazio — defina TOTEM_ARMARIO_ID=3")
    else:
        erro(f"TOTEM_ARMARIO_ID={totem_id} — esperado 3 (Matriz)")

    token_env = (config.ESP32_TOKEN or "").strip()
    if not token_env:
        aviso("ESP32_TOKEN não definido no .env (opcional se firmware/banco alinhados)")
    elif token_esperado and token_env != token_esperado:
        aviso(f"ESP32_TOKEN no .env difere do token oficial ({token_env[:8]}...)")
    elif token_env:
        ok(f"ESP32_TOKEN definido ({token_env[:8]}...)")

    if config.DATABASE_URL:
        erro(
            "DATABASE_URL definido — servidor usa PostgreSQL, "
            "scripts de bancada gravam SQLite. Remova DATABASE_URL= na bancada."
        )
    else:
        ok("Sem DATABASE_URL — SQLite (correto na bancada)")

    sim = os.getenv("ESP32_MODO_SIMULACAO", "0").strip()
    if sim in ("1", "true", "True"):
        aviso("ESP32_MODO_SIMULACAO=1 — relés simulados, não hardware real")
    else:
        ok("ESP32_MODO_SIMULACAO=0 (hardware real)")


def verificar_banco(token_esperado):
    print("\n--- Banco de dados ---")
    from db.connection import get_engine

    engine = get_engine()
    if engine == "postgresql":
        erro(f"Engine PostgreSQL ativa — na bancada use SQLite (sem DATABASE_URL)")
    else:
        db_path = ROOT / "database" / "elevalocker.db"
        ok(f"SQLite ({db_path.name})")

    with BaseRepository.get_connection() as conn:
        arm = conn.execute(
            "SELECT id, nome, status FROM armarios WHERE nome = ? LIMIT 1",
            (NOME_ARMARIO,),
        ).fetchone()
        if arm:
            ok(f"Armário '{NOME_ARMARIO}' id={arm['id']}")
            if str(arm["id"]) != ARMARIO_ID_ESPERADO:
                aviso(f"Armário Matriz id={arm['id']} (esperado id=3 no .env)")
        else:
            erro(f"Armário '{NOME_ARMARIO}' não encontrado — rode setup_oficial.py")

        bancada = conn.execute(
            "SELECT id FROM armarios WHERE nome = 'Bancada Teste' LIMIT 1"
        ).fetchone()
        if bancada:
            aviso(
                f"Armário 'Bancada Teste' id={bancada['id']} ainda existe — "
                "rode limpar_bancada_teste.py"
            )

        esps = conn.execute("""
            SELECT e.id, e.nome, e.ip, e.token, e.status, e.armario, a.nome AS armario_nome
            FROM esp32 e
            LEFT JOIN armarios a ON a.id = e.armario
            ORDER BY e.id
        """).fetchall()

        print(f"\n  ESP cadastrados: {len(esps)}")
        oficial = None
        duplicados = []
        for e in esps:
            linha = f"id={e['id']} {e['nome']} | {e['ip'] or '—'} | {e['armario_nome'] or '—'}"
            print(f"    {linha}")
            if e["nome"] == NOME_ESP:
                oficial = e
            elif e["armario_nome"] == "Bancada Teste" or "Bancada" in (e["nome"] or ""):
                duplicados.append(e)

        if not oficial:
            erro(f"ESP '{NOME_ESP}' não encontrado — rode setup_oficial.py")
        else:
            ok(f"ESP oficial id={oficial['id']} ip={oficial['ip'] or '—'}")
            if oficial["armario_nome"] != NOME_ARMARIO:
                erro(f"ESP oficial ligado ao armário '{oficial['armario_nome']}' — deve ser Matriz")
            if token_esperado:
                if (oficial["token"] or "").strip() == token_esperado.strip():
                    ok("Token banco = token esperado")
                else:
                    erro(
                        f"Token banco difere — rode corrigir_token_esp.py "
                        f"(banco: {(oficial['token'] or '')[:8]}...)"
                    )

        if len(esps) > 1:
            aviso(f"{len(esps)} ESPs no banco — ideal: só 1 (Matriz). Rode limpar_bancada_teste.py")
        for d in duplicados:
            aviso(f"ESP de teste id={d['id']} ({d['nome']}) — remover com limpar_bancada_teste.py")

        if oficial:
            comps = conn.execute(
                "SELECT COUNT(*) AS n FROM compartimentos WHERE armario = ?",
                (oficial["armario"],),
            ).fetchone()["n"]
            if comps >= 8:
                ok(f"{comps} compartimentos no armário Matriz")
            else:
                aviso(f"Só {comps} compartimentos — rode setup_oficial.py --portas 8")


def verificar_firmware():
    print("\n--- Firmware ---")
    for path, label in ((FIRMWARE_DST, "Arduino"), (FIRMWARE_SRC, "fonte")):
        if not path.exists():
            erro(f"{label}: {path.relative_to(ROOT)} não encontrado")
            continue
        texto = path.read_text(encoding="utf-8")
        checks = {
            "SENSOR_GPIO": "sensores de porta",
            "RELE_ATIVO_LOW": "placa BESTER (LOW=ligado)",
            "ESP32_TOKEN": "token configurável",
        }
        faltando = [nome for nome in checks if nome not in texto]
        if faltando:
            erro(f"{label}: faltam {', '.join(faltando)} — branch/firmware antigo?")
        else:
            ok(f"{label}: SENSOR_GPIO + RELE_ATIVO_LOW presentes")

    if FIRMWARE_SRC.exists() and FIRMWARE_DST.exists():
        if FIRMWARE_SRC.read_bytes() == FIRMWARE_DST.read_bytes():
            ok("Firmware fonte = pasta Arduino (sincronizados)")
        else:
            aviso("Firmware fonte ≠ pasta Arduino — rode atualizar_matriz.py --so-firmware")


def main():
    parser = argparse.ArgumentParser(description="Verifica instalação Matriz ELEVA LOCKER")
    parser.add_argument("--token", default=os.getenv("ESP32_TOKEN", "2e5bb4db71d8330be8bae43b13ac19f6"))
    parser.add_argument("--strict", action="store_true", help="Exit 1 se houver qualquer problema")
    args = parser.parse_args()

    print("=" * 60)
    print("  VERIFICAR MATRIZ — ELEVA LOCKER")
    print("=" * 60)

    verificar_env(args.token)
    verificar_banco(args.token)
    verificar_firmware()

    print("\n" + "=" * 60)
    if problemas:
        print(f"  {len(problemas)} PROBLEMA(S) — corrija antes de operar")
        for p in problemas:
            print(f"    • {p}")
    elif avisos:
        print(f"  OK com {len(avisos)} aviso(s)")
    else:
        print("  TUDO OK — pronto para depósito/retirada")
    print("=" * 60)
    print("\n  Atualizar:  tools\\atualizar_matriz.bat")
    print("  Totem:      http://192.168.16.130:15000/totem/3")
    print("=" * 60)

    if problemas or (args.strict and avisos):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
