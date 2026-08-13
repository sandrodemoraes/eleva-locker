#!/usr/bin/env python3
"""
CONSERTAR BANCADA — um script, zero margem de erro.

Para servidor, força SQLite, recria armário Matriz, token, totem e sobe 1 app.py.

Uso:
  python tools/consertar_bancada.py
  python tools/consertar_bancada.py --no-start
"""
import argparse
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

from env_bancada import aplicar_bancada_processo, env_subprocess, garantir_bancada_env

aplicar_bancada_processo()

IP_ESP = "192.168.16.162"
TOKEN = "2e5bb4db71d8330be8bae43b13ac19f6"
NOME_ESP = "ESP Matriz 8ch"


def run(cmd, **kw):
    show = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f">>> {show}")
    return subprocess.run(cmd, cwd=ROOT, env=env_subprocess(), text=True, **kw)


def parar():
    print("\n[1] Parando servidor...")
    run([sys.executable, "tools/parar_servidor.py"])


def fix_env():
    print("\n[2] .env bancada (SQLite + ELEVA_BANCADA=1)...")
    garantir_bancada_env()
    # Token correto
    env_path = ROOT / ".env"
    texto = env_path.read_text(encoding="utf-8")
    if f"ESP32_TOKEN={TOKEN}" not in texto:
        from env_bancada import definir_chave
        linhas = definir_chave(texto.splitlines(), "ESP32_TOKEN", TOKEN)
        env_path.write_text("\n".join(linhas).rstrip() + "\n", encoding="utf-8")
    print("    OK  ELEVA_BANCADA=1, DATABASE_URL off, ESP32_TOKEN alinhado")


def setup():
    print(f"\n[3] Setup oficial (ESP {IP_ESP})...")
    return run([
        sys.executable, "tools/setup_oficial.py",
        "--ip-esp", IP_ESP, "--portas", "8",
    ]).returncode == 0


def corrigir_totem():
    print("\n[4] Totem + TOTEM_ARMARIO_ID...")
    return run([sys.executable, "tools/corrigir_totem_armario.py", "--sem-setup"]).returncode == 0


def limpar():
    print("\n[5] Backup vínculos usuários (antes de limpar teste)...")
    run([sys.executable, "tools/backup_vinculos_usuarios.py"])
    print("\n[5b] Limpar ESP duplicados...")
    run([sys.executable, "tools/limpar_bancada_teste.py"])


def token():
    print("\n[6] Token ESP no banco...")
    return run([
        sys.executable, "tools/corrigir_token_esp.py",
        "--token", TOKEN, "--nome-esp", NOME_ESP, "--sem-teste",
    ]).returncode == 0


def obter_armario_id():
    aplicar_bancada_processo()
    from database import criar_banco
    criar_banco()
    from repositories.base_repository import BaseRepository
    with BaseRepository.get_connection() as conn:
        row = conn.execute(
            "SELECT id FROM armarios WHERE nome = 'ELEVA Locker Matriz' LIMIT 1"
        ).fetchone()
    return row["id"] if row else None


def verificar_banco():
    aplicar_bancada_processo()
    from db.connection import get_engine
    from database import criar_banco
    criar_banco()
    from repositories.base_repository import BaseRepository

    engine = get_engine()
    print(f"\n[7] Verificação — engine={engine}")
    with BaseRepository.get_connection() as conn:
        arm = conn.execute("SELECT COUNT(*) AS n FROM armarios").fetchone()["n"]
        esp = conn.execute("SELECT COUNT(*) AS n FROM esp32").fetchone()["n"]
        comp = conn.execute("SELECT COUNT(*) AS n FROM compartimentos").fetchone()["n"]
    print(f"    Armários: {arm} | ESP: {esp} | Compartimentos: {comp}")
    if engine != "sqlite":
        print("    ERRO: não está em SQLite!")
        return False
    if arm < 1 or esp < 1 or comp < 8:
        print("    ERRO: dados incompletos no banco")
        return False
    return True


def iniciar():
    print("\n[8] Iniciando app.py (1 instância)...")
    env = env_subprocess()
    env.pop("SKIP_BACKUP", None)
    if sys.platform == "win32":
        cmd = f'start "ELEVA LOCKER" cmd /k "cd /d {ROOT} && set ELEVA_BANCADA=1 && set DATABASE_URL= && python app.py"'
        subprocess.Popen(cmd, shell=True, cwd=ROOT)
    else:
        subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env)
    print("    Aguardando API...")
    fim = time.time() + 45
    while time.time() < fim:
        try:
            urllib.request.urlopen("http://127.0.0.1:15000/totem/versao", timeout=3)
            print("    OK  servidor respondendo")
            return True
        except urllib.error.URLError:
            time.sleep(2)
    print("    AVISO: timeout — verifique janela do app.py")
    return False


def main():
    parser = argparse.ArgumentParser(description="Conserta bancada Matriz (SQLite único)")
    parser.add_argument("--no-start", action="store_true", help="Não reinicia app.py")
    args = parser.parse_args()

    print("=" * 60)
    print("  CONSERTAR BANCADA — ELEVA LOCKER MATRIZ")
    print("=" * 60)

    parar()
    fix_env()
    if not setup():
        print("\nERRO: setup_oficial falhou")
        return 1
    if not corrigir_totem():
        print("\nERRO: corrigir totem falhou")
        return 1
    limpar()
    token()
    print("\n[6b] Usuários do armário (operadores + moradores)...")
    run([sys.executable, "tools/restaurar_usuarios_armario.py"])

    if not verificar_banco():
        return 1

    arm_id = obter_armario_id()
    if not args.no_start:
        iniciar()
        run([
            sys.executable, "tools/corrigir_token_esp.py",
            "--token", TOKEN, "--nome-esp", NOME_ESP,
        ])

    print("\n" + "=" * 60)
    print("  BANCADA CONSERTADA")
    print("=" * 60)
    print(f"""
  Banco:    SQLite (ELEVA_BANCADA=1 no .env)
  Armário:  id={arm_id}
  Totem:    http://192.168.16.130:15000/totem/{arm_id}
  Painel:   http://192.168.16.130:15000/armarios
  Token:    {TOKEN}

  IMPORTANTE: use sempre tools\\consertar_bancada.bat ou atualizar_matriz.bat
  NÃO rode docker web + app.py ao mesmo tempo.
""")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
