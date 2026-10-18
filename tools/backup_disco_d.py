#!/usr/bin/env python3
"""Backup ELEVA LOCKER para disco D: — rotativo + espelho do projeto."""

import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

os.environ.setdefault("BACKUP_DIR", r"D:\ElevaLockerBackup\rotativo")

import config  # noqa: E402
from services.backup.backup_service import BackupService  # noqa: E402

DISCO_D = Path(r"D:\ElevaLockerBackup")
ESPELHO = DISCO_D / "projeto"
ROTATIVO = DISCO_D / "rotativo"

IGNORAR = {
    "__pycache__",
    ".git",
    "venv",
    ".venv",
    "node_modules",
    "backups",
}


def espelhar_projeto():
    ESPELHO.mkdir(parents=True, exist_ok=True)
    copiados = 0

    for item in ROOT.iterdir():
        if item.name in IGNORAR:
            continue
        dest = ESPELHO / item.name
        try:
            if item.is_dir():
                if dest.exists():
                    shutil.rmtree(dest)
                shutil.copytree(
                    item,
                    dest,
                    ignore=shutil.ignore_patterns(*IGNORAR),
                )
            else:
                shutil.copy2(item, dest)
            copiados += 1
        except Exception as erro:
            print(f"  AVISO: {item.name} — {erro}")

    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    (ESPELHO / "_ultimo_backup.txt").write_text(stamp, encoding="utf-8")
    return copiados


def main():
    print("=" * 50)
    print("  ELEVA LOCKER — Backup disco D:")
    print("=" * 50)
    print()

    if not Path("D:/").exists():
        print("ERRO: Disco D: nao encontrado.")
        return 1

    DISCO_D.mkdir(parents=True, exist_ok=True)
    ROTATIVO.mkdir(parents=True, exist_ok=True)

    config.BACKUP_DIR = str(ROTATIVO)

    print("1/2 Backup rotativo (banco, .env, uploads)...")
    ok = BackupService.criar_backup(forcar=True)
    if ok:
        print(f"   OK: {ROTATIVO}\\backup_01")
    else:
        print("   AVISO: backup rotativo nao criado — veja mensagens acima")
        return 1

    print()
    print("2/2 Espelho completo do projeto...")
    n = espelhar_projeto()
    print(f"   {n} itens copiados para {ESPELHO}")

    print()
    print("OK — Backup concluido!")
    print(f"  Data:     {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"  Rotativo: {ROTATIVO}\\backup_01")
    print(f"  Espelho:  {ESPELHO}")
    print(f"  Banco:    {ROTATIVO}\\backup_01\\database\\elevalocker.db")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
