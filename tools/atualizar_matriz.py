#!/usr/bin/env python3
"""
Atualização simplificada — instalação oficial ELEVA Locker Matriz (8 portas).

Faz em sequência:
  1. Para servidor na 15000
  2. Backup OBRIGATÓRIO (banco + .env) — aborta se falhar
  3. git pull
  4. Sincroniza firmware na pasta Arduino
  5. setup_oficial (armário + ESP + 8 compartimentos)
  6. Remove ESP/armário de teste duplicados
  7. Reinicia app.py
  8. Alinha token ESP no banco + verificação final

Uso:
  python tools/atualizar_matriz.py
  python tools/atualizar_matriz.py --branch cursor/fix-retirada-rele-c05c
  python tools/atualizar_matriz.py --so-firmware
  python tools/atualizar_matriz.py --no-restart
  python tools/atualizar_matriz.py --verificar
"""
import argparse
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

BRANCH_PADRAO = "cursor/fix-retirada-rele-c05c"
IP_ESP_PADRAO = "192.168.16.162"
NOME_ESP = "ESP Matriz 8ch"
TOKEN_PADRAO = "2e5bb4db71d8330be8bae43b13ac19f6"

FIRMWARE_SRC = ROOT / "firmware" / "elevalocker_sync.ino"
FIRMWARE_DST = ROOT / "firmware" / "elevalocker_sync" / "elevalocker_sync.ino"


def run(cmd, **kwargs):
    show = cmd if isinstance(cmd, str) else " ".join(str(c) for c in cmd)
    print(f">>> {show}")
    return subprocess.run(cmd, cwd=ROOT, text=True, **kwargs)


def verificar(token, strict=False):
    args = [sys.executable, "tools/verificar_matriz.py", "--token", token]
    if strict:
        args.append("--strict")
    return run(args).returncode == 0


def parar():
    sys.path.insert(0, str(ROOT / "tools"))
    from parar_servidor import parar_app_py, parar_docker_web, parar_porta

    print("\n[1] Parando servidor...")
    parar_docker_web()
    parar_app_py()
    parar_porta()


def backup_obrigatorio():
    print("\n[2] Backup OBRIGATÓRIO (banco + .env)...")
    print("    Se falhar, a atualização é ABORTADA.")
    r = run([sys.executable, "tools/backup_obrigatorio.py"])
    if r.returncode != 0:
        print("\n" + "!" * 60)
        print("  ATUALIZAÇÃO CANCELADA — backup não concluído.")
        print("  Corrija e rode: tools\\backup_obrigatorio.bat")
        print("!" * 60)
        return False
    return True


def git_pull(branch):
    print(f"\n[3] Git pull ({branch})...")
    run(["git", "fetch", "origin", branch], check=False)
    atual = run(["git", "rev-parse", "--abbrev-ref", "HEAD"], capture_output=True)
    if (atual.stdout or "").strip() != branch:
        run(["git", "checkout", branch], check=False)
    r = run(["git", "pull", "origin", branch], capture_output=True)
    if r.returncode != 0:
        print((r.stderr or r.stdout or "git pull falhou").strip())
        return False
    r = run(["git", "log", "-1", "--oneline"], capture_output=True)
    if r.stdout:
        print(f"    {r.stdout.strip()}")
    return True


def sincronizar_firmware():
    print("\n[4] Sincronizando firmware Arduino...")
    if not FIRMWARE_SRC.exists():
        print(f"    ERRO: {FIRMWARE_SRC} não encontrado")
        return False
    FIRMWARE_DST.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIRMWARE_SRC, FIRMWARE_DST)
    texto = FIRMWARE_DST.read_text(encoding="utf-8")
    ok = "SENSOR_GPIO" in texto and "RELE_ATIVO_LOW" in texto
    print(f"    Copiado → {FIRMWARE_DST.relative_to(ROOT)}")
    print(f"    SENSOR_GPIO: {'OK' if ok else 'FALTANDO — branch errada?'}")
    return ok


def setup_oficial(ip_esp):
    print(f"\n[5] Setup oficial (ESP {ip_esp})...")
    return run([
        sys.executable, "tools/setup_oficial.py",
        "--ip-esp", ip_esp, "--portas", "8",
    ]).returncode == 0


def limpar_teste():
    print("\n[6] Removendo ESP/armário de teste duplicados...")
    return run([sys.executable, "tools/limpar_bancada_teste.py"]).returncode == 0


def alinhar_token(token, url_servidor):
    print("\n[8] Token ESP no banco...")
    return run([
        sys.executable, "tools/corrigir_token_esp.py",
        "--token", token,
        "--nome-esp", NOME_ESP,
        "--url", url_servidor,
    ]).returncode == 0


def reiniciar():
    print("\n[7] Reiniciando servidor...")
    env = os.environ.copy()
    env.pop("SKIP_BACKUP", None)
    if sys.platform == "win32":
        cmd = f'start "ELEVA LOCKER" cmd /k "cd /d {ROOT} && python app.py"'
        subprocess.Popen(cmd, shell=True, cwd=ROOT, env=env)
        print("    Nova janela: python app.py")
    else:
        subprocess.Popen([sys.executable, "app.py"], cwd=ROOT, env=env)
    return True


def aguardar_api(segundos=60):
    print("\n    Aguardando http://127.0.0.1:15000/totem/versao ...")
    fim = time.time() + segundos
    while time.time() < fim:
        try:
            with urllib.request.urlopen("http://127.0.0.1:15000/totem/versao", timeout=3) as resp:
                print(f"    HTTP {resp.status} — servidor OK")
                return True
        except urllib.error.URLError:
            time.sleep(2)
    print("    Timeout — abra manualmente: python app.py")
    return False


def imprimir_resumo(token):
    print("\n" + "=" * 60)
    print("  ATUALIZAÇÃO MATRIZ — concluída")
    print("=" * 60)
    print(f"""
  Backup:   backups\\backup_01 (+ D:\\ElevaLockerBackup se D: existir)
  Painel:   http://192.168.16.130:15000/armarios/3
  Totem:    http://192.168.16.130:15000/totem/3
  Bancada:  http://192.168.16.130:15000/esp32/bancada

  Arduino:  firmware\\elevalocker_sync\\elevalocker_sync.ino
  Token:    {token}

  .env deve ter:
    TOTEM_ARMARIO_ID=3
    ESP32_TOKEN={token}
    (sem DATABASE_URL = SQLite)

  Teste ESP: http://192.168.16.162/?token={token}

  Se mudou firmware → Upload no Arduino IDE (fechar Serial Monitor antes).
  Verificar: tools\\verificar_matriz.bat
""")


def main():
    parser = argparse.ArgumentParser(description="Atualização simplificada Matriz 8ch")
    parser.add_argument("--branch", default=BRANCH_PADRAO)
    parser.add_argument("--ip-esp", default=IP_ESP_PADRAO)
    parser.add_argument("--token", default=TOKEN_PADRAO)
    parser.add_argument("--url", default="http://127.0.0.1:15000")
    parser.add_argument("--so-firmware", action="store_true", help="Só copia firmware Arduino")
    parser.add_argument("--no-restart", action="store_true")
    parser.add_argument("--no-git", action="store_true")
    parser.add_argument("--verificar", action="store_true", help="Só roda verificar_matriz.py")
    parser.add_argument("--sem-limpar", action="store_true", help="Não remove bancada teste")
    args = parser.parse_args()

    print("=" * 60)
    print("  ELEVA LOCKER — Atualizar Matriz (8 portas)")
    print("=" * 60)

    if args.verificar:
        return 0 if verificar(args.token) else 1

    if args.so_firmware:
        if not backup_obrigatorio():
            return 1
        ok_fw = sincronizar_firmware()
        verificar(args.token)
        return 0 if ok_fw else 1

    parar()

    if not backup_obrigatorio():
        return 1

    if not args.no_git and not git_pull(args.branch):
        return 1

    if not sincronizar_firmware():
        return 1

    if not setup_oficial(args.ip_esp):
        print("    AVISO: setup_oficial falhou — verifique acima")

    if not args.sem_limpar:
        limpar_teste()

    if args.no_restart:
        print("\n    Servidor NÃO reiniciado (--no-restart).")
        print("    Depois: python app.py")
        print("    Depois: python tools/corrigir_token_esp.py --token ...")
        verificar(args.token)
        imprimir_resumo(args.token)
        return 0

    reiniciar()
    if aguardar_api():
        alinhar_token(args.token, args.url)

    print("\n[9] Verificação final...")
    verificar(args.token)
    imprimir_resumo(args.token)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
