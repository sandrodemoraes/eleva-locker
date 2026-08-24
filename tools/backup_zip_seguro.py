#!/usr/bin/env python3
"""
Backup ZIP seguro — ELEVA LOCKER

Cria arquivo .zip completo em D:\\ElevaLockerBackup\\zip\\
Inclui: codigo, .env, banco SQLite, firmware, docs
Exclui: __pycache__, venv, logs antigos (opcional)

Uso:
  python tools/backup_zip_seguro.py
  python tools/backup_zip_seguro.py --sem-env        # ZIP sem .env (compartilhar)
  python tools/backup_zip_seguro.py --origem D:\\ElevaLockerBackup\\projeto
"""
from __future__ import annotations

import argparse
import os
import shutil
import sys
import zipfile
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DISCO_D = Path(r"D:\ElevaLockerBackup")
ZIP_DIR = DISCO_D / "zip"
MANIFEST_NAME = "_BACKUP_INFO.txt"

IGNORAR_DIRS = {
    "__pycache__",
    ".pytest_cache",
    "venv",
    ".venv",
    "node_modules",
    ".cursor",
    "htmlcov",
}
IGNORAR_ARQUIVOS = {
    ".pyc",
    ".pyo",
    ".DS_Store",
    "Thumbs.db",
}
IGNORAR_PASTAS_OPCIONAL = {"logs", "backups", ".git"}


def _deve_ignorar(path: Path, incluir_git: bool, incluir_logs: bool) -> bool:
    partes = set(path.parts)
    if partes & IGNORAR_DIRS:
        return True
    if not incluir_git and ".git" in partes:
        return True
    if not incluir_logs and "logs" in partes:
        return True
    if path.suffix.lower() in IGNORAR_ARQUIVOS:
        return True
    return False


def _criar_backup_banco() -> Path | None:
    """Garante backup_01 atualizado antes do ZIP."""
    try:
        from services.backup.backup_service import BackupService

        ok, msg = BackupService.criar_backup_obrigatorio()
        if ok:
            return Path(msg)
    except Exception as exc:
        print(f"  AVISO: backup rotativo — {exc}")
    return None


def _adicionar_arquivo(zf: zipfile.ZipFile, arquivo: Path, arcname: str) -> None:
    zf.write(arquivo, arcname)
    print(f"    + {arcname}")


def _compactar_origem(
    origem: Path,
    destino_zip: Path,
    incluir_env: bool,
    incluir_git: bool,
    incluir_logs: bool,
) -> tuple[int, int]:
    arquivos = 0
    bytes_total = 0

    with zipfile.ZipFile(
        destino_zip,
        "w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=6,
    ) as zf:
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        info = (
            f"ELEVA LOCKER — Backup ZIP\n"
            f"Data: {stamp}\n"
            f"Origem: {origem}\n"
            f"Inclui .env: {'sim' if incluir_env else 'nao'}\n"
            f"Inclui .git: {'sim' if incluir_git else 'nao'}\n\n"
            f"RESTAURAR:\n"
            f"1. Extrair ZIP em pasta vazia (ex: C:\\ElevaLocker)\n"
            f"2. pip install -r requirements.txt\n"
            f"3. Conferir .env\n"
            f"4. python app.py\n"
        )
        zf.writestr(MANIFEST_NAME, info)

        for item in sorted(origem.rglob("*")):
            if not item.is_file():
                continue
            rel = item.relative_to(origem)
            if _deve_ignorar(item, incluir_git, incluir_logs):
                continue
            if not incluir_env and item.name == ".env":
                continue
            zf.write(item, rel.as_posix())
            arquivos += 1
            bytes_total += item.stat().st_size

        # Banco atualizado de backups/backup_01 (se existir no projeto)
        backup_db = ROOT / "backups" / "backup_01" / "database" / "elevalocker.db"
        if backup_db.exists():
            arc = "backups/backup_01/database/elevalocker.db"
            if arc not in zf.namelist():
                _adicionar_arquivo(zf, backup_db, arc)
                arquivos += 1
                bytes_total += backup_db.stat().st_size

        env_backup = ROOT / "backups" / "backup_01" / ".env"
        if incluir_env and env_backup.exists():
            arc = "backups/backup_01/.env"
            if arc not in zf.namelist():
                _adicionar_arquivo(zf, env_backup, arc)
                arquivos += 1
                bytes_total += env_backup.stat().st_size

    return arquivos, bytes_total


def _rotacionar(max_manter: int = 10) -> None:
    zips = sorted(ZIP_DIR.glob("ElevaLocker-*.zip"), key=lambda p: p.stat().st_mtime)
    while len(zips) > max_manter:
        velho = zips.pop(0)
        print(f"  Removendo antigo: {velho.name}")
        velho.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description="Backup ZIP seguro ELEVA LOCKER")
    parser.add_argument(
        "--origem",
        default="",
        help="Pasta a compactar (padrao: projeto atual ou D:\\ElevaLockerBackup\\projeto)",
    )
    parser.add_argument(
        "--sem-env",
        action="store_true",
        help="Nao incluir .env no ZIP (para compartilhar)",
    )
    parser.add_argument(
        "--sem-git",
        action="store_true",
        help="Nao incluir pasta .git (ZIP menor)",
    )
    parser.add_argument(
        "--com-logs",
        action="store_true",
        help="Incluir pasta logs/",
    )
    args = parser.parse_args()

    if args.origem:
        origem = Path(args.origem)
    elif (DISCO_D / "projeto").is_dir():
        origem = DISCO_D / "projeto"
    else:
        origem = ROOT

    if not origem.is_dir():
        print(f"ERRO: pasta nao encontrada: {origem}")
        return 1

    if not Path("D:/").exists():
        ZIP_DIR_LOCAL = ROOT / "backups" / "zip"
        ZIP_DIR_LOCAL.mkdir(parents=True, exist_ok=True)
        zip_dest = ZIP_DIR_LOCAL
        print("AVISO: Disco D: nao encontrado — salvando em backups/zip/")
    else:
        zip_dest = ZIP_DIR
        zip_dest.mkdir(parents=True, exist_ok=True)

    print("=" * 55)
    print("  ELEVA LOCKER — Backup ZIP seguro")
    print("=" * 55)
    print(f"  Origem: {origem}")
    print()

    print("1/3 Backup banco + .env (backup_01)...")
    dest = _criar_backup_banco()
    if dest:
        print(f"    OK: {dest}")
    else:
        print("    AVISO: use backups/ existente ou .env na origem")

    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    sufixo = "completo" if not args.sem_env else "sem-env"
    arquivo_zip = zip_dest / f"ElevaLocker-{sufixo}-{stamp}.zip"

    print()
    print(f"2/3 Compactando → {arquivo_zip.name} ...")
    n, tam = _compactar_origem(
        origem,
        arquivo_zip,
        incluir_env=not args.sem_env,
        incluir_git=not args.sem_git,
        incluir_logs=args.com_logs,
    )
    mb = arquivo_zip.stat().st_size / (1024 * 1024)
    print(f"    {n} arquivos | ZIP: {mb:.1f} MB")

    if zip_dest == ZIP_DIR:
        print()
        print("3/3 Rotacionando (mantem ultimos 10)...")
        _rotacionar(10)

    print()
    print("OK — Backup ZIP concluido!")
    print(f"  Arquivo: {arquivo_zip}")
    print()
    print("SEGURANCA:")
    print("  - Guarde copia em nuvem (Google Drive / OneDrive) ou HD externo")
    print("  - ZIP com .env contem SENHAS — nao envie por WhatsApp/e-mail publico")
    print("  - Para INPI/compartilhar: use --sem-env")
    return 0


if __name__ == "__main__":
    sys.exit(main())
