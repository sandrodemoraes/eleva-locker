#!/usr/bin/env python3
"""
Restaura elevalocker_sync.ino completo (~700 linhas) a partir de backup ou git.

Uso:
  py tools/restaurar_firmware.py
  py tools/restaurar_firmware.py --listar
"""
import argparse
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DEST = os.path.join(ROOT, "firmware", "elevalocker_sync", "elevalocker_sync.ino")
SRC = os.path.join(ROOT, "firmware", "elevalocker_sync.ino")

FONTES = [
    ("backup pré-update", os.path.join(ROOT, "backups", "_pre_update_firmware.ino")),
    ("backup #1", os.path.join(ROOT, "backups", "backup_01", "elevalocker_sync.ino.bak")),
    ("firmware raiz (git)", SRC),
]


def linhas_validas(caminho):
    if not os.path.isfile(caminho):
        return 0, False
    with open(caminho, encoding="utf-8", errors="replace") as f:
        texto = f.read()
    ok = "void setup()" in texto and "SENSOR_GPIO" in texto
    return texto.count("\n") + 1, ok


def listar_fontes():
    print("\nFontes de firmware disponíveis:\n")
    for nome, caminho in FONTES:
        n, ok = linhas_validas(caminho)
        status = "OK" if ok else ("ausente" if n == 0 else f"incompleto ({n} linhas)")
        print(f"  [{status:20}] {nome}")
        print(f"                       {caminho}")
    n_dest, ok_dest = linhas_validas(DEST)
    print(f"\n  Arquivo atual Arduino: {n_dest} linhas — {'OK' if ok_dest else 'INCOMPLETO'}")
    print(f"                       {DEST}\n")


def restaurar_git():
    try:
        r = subprocess.run(
            [
                "git", "checkout", "HEAD", "--",
                "firmware/elevalocker_sync.ino",
                "firmware/elevalocker_sync/elevalocker_sync.ino",
            ],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if r.returncode == 0:
            n, ok = linhas_validas(DEST)
            if ok or linhas_validas(SRC)[1]:
                os.makedirs(os.path.dirname(DEST), exist_ok=True)
                if linhas_validas(SRC)[1]:
                    shutil.copy2(SRC, DEST)
                return True, "git checkout HEAD"
    except FileNotFoundError:
        pass
    return False, ""


def main():
    parser = argparse.ArgumentParser(description="Restaurar firmware ESP32 completo")
    parser.add_argument("--listar", action="store_true", help="Lista fontes e sai")
    args = parser.parse_args()

    if args.listar:
        listar_fontes()
        return

    print("=" * 60)
    print("  RESTAURAR FIRMWARE elevalocker_sync.ino")
    print("=" * 60)

    n_atual, ok_atual = linhas_validas(DEST)
    if ok_atual:
        print(f"\nFirmware já OK ({n_atual} linhas): {DEST}")
        return

    if n_atual:
        print(f"\nArquivo atual incompleto: {n_atual} linhas")

    for nome, caminho in FONTES:
        n, ok = linhas_validas(caminho)
        if not ok:
            continue
        os.makedirs(os.path.dirname(DEST), exist_ok=True)
        shutil.copy2(caminho, DEST)
        print(f"\nRestaurado de: {nome}")
        print(f"  {caminho}")
        print(f"  → {DEST}")
        print(f"  {n} linhas — void setup() + SENSOR_GPIO OK")
        print("\nPróximo: abra no Arduino IDE e ajuste ESP32_TOKEN + RELE_ATIVO_LOW")
        return

    ok_git, msg = restaurar_git()
    if ok_git:
        n, _ = linhas_validas(DEST)
        print(f"\nRestaurado via {msg} ({n} linhas)")
        print(f"  → {DEST}")
        return

    print("\nNenhuma fonte válida encontrada.")
    print("  Rode: git pull")
    print("  Ou copie manualmente de outro PC com ElevaLocker completo")
    listar_fontes()
    sys.exit(1)


if __name__ == "__main__":
    main()
