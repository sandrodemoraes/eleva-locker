#!/usr/bin/env python3
"""Backup ZIP completo em D:\\ElevaLockerBackup\\zip\\"""

import argparse
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DISCO_D = Path(r"D:\ElevaLockerBackup")
ZIP_DIR = DISCO_D / "zip"
MANIFEST = "_BACKUP_INFO.txt"

IGNORAR_DIRS = {"__pycache__", ".pytest_cache", "venv", ".venv", "node_modules", ".cursor"}
IGNORAR_EXT = {".pyc", ".pyo"}


def _ignorar(path: Path, incluir_git: bool, incluir_logs: bool) -> bool:
    partes = set(path.parts)
    if partes & IGNORAR_DIRS:
        return True
    if not incluir_git and ".git" in partes:
        return True
    if not incluir_logs and "logs" in partes:
        return True
    return path.suffix.lower() in IGNORAR_EXT


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sem-env", action="store_true")
    parser.add_argument("--sem-git", action="store_true", default=True)
    args = parser.parse_args()

    if not Path("D:/").exists():
        print("ERRO: Disco D: nao encontrado.")
        return 1

    import os
    os.environ["BACKUP_DIR"] = r"D:\ElevaLockerBackup\rotativo"

    from services.backup.backup_service import BackupService

    print("1/2 Backup banco + .env...")
    if not BackupService.criar_backup(forcar=True):
        print("   ERRO ao criar backup rotativo.")
        return 1

    origem = ROOT
    ZIP_DIR.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    zip_path = ZIP_DIR / f"ElevaLocker-{stamp}.zip"

    print(f"2/2 Compactando {zip_path.name}...")
    n = 0
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        info = f"ELEVA LOCKER backup {datetime.now()}\nOrigem: {origem}\n"
        zf.writestr(MANIFEST, info)
        for item in sorted(origem.rglob("*")):
            if not item.is_file():
                continue
            if _ignorar(item, incluir_git=not args.sem_git, incluir_logs=False):
                continue
            if args.sem_env and item.name == ".env":
                continue
            rel = item.relative_to(origem).as_posix()
            zf.write(item, rel)
            n += 1

    mb = zip_path.stat().st_size / (1024 * 1024)
    print()
    print(f"OK — {n} arquivos | {mb:.1f} MB")
    print(f"  {zip_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
