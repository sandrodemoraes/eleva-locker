#!/usr/bin/env python3
"""
Backup OBRIGATÓRIO antes de qualquer atualização.

Cria backup local (backups/backup_01) com banco + .env e valida integridade.
Se D: existir, copia também para D:\\ElevaLockerBackup.

Aborta (exit 1) se qualquer etapa obrigatória falhar.

Uso:
  python tools/backup_obrigatorio.py
  python tools/backup_obrigatorio.py --sem-disco-d
"""
import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from services.backup.backup_service import BackupService  # noqa: E402


def backup_local():
    print("\n[backup] Local (backups/backup_01)...")
    ok, msg = BackupService.criar_backup_obrigatorio()
    if not ok:
        print(f"    ERRO: {msg}")
        return False
    destino = Path(msg)
    db = destino / "database" / "elevalocker.db"
    env = destino / ".env"
    print(f"    OK  {destino}")
    print(f"    OK  banco {db.stat().st_size // 1024} KB")
    print(f"    OK  .env {env.stat().st_size} bytes")
    return True


def backup_disco_d():
    script = ROOT / "tools" / "backup_disco_d.py"
    if not script.exists():
        print("\n[backup] D: — script backup_disco_d.py não encontrado (só local)")
        return True

    if not Path("D:/").exists():
        print("\n[backup] D: não encontrado — pulando espelho externo")
        return True

    print("\n[backup] Disco D: (rotativo + espelho projeto)...")
    import subprocess
    r = subprocess.run([sys.executable, str(script)], cwd=ROOT)
    if r.returncode != 0:
        print("    ERRO: backup no D: falhou")
        return False
    print("    OK  D:\\ElevaLockerBackup")
    return True


def main():
    parser = argparse.ArgumentParser(description="Backup obrigatório ELEVA LOCKER")
    parser.add_argument("--sem-disco-d", action="store_true", help="Só backup local")
    args = parser.parse_args()

    print("=" * 60)
    print("  BACKUP OBRIGATÓRIO — ELEVA LOCKER")
    print("=" * 60)

    if not (ROOT / ".env").exists():
        print("\nERRO: .env não encontrado — crie antes de atualizar.")
        return 1

    if not (ROOT / "database" / "elevalocker.db").exists():
        print("\nERRO: database/elevalocker.db não encontrado.")
        return 1

    if not backup_local():
        print("\n" + "=" * 60)
        print("  FALHA — atualização BLOQUEADA (sem backup válido)")
        print("=" * 60)
        return 1

    if not args.sem_disco_d and not backup_disco_d():
        print("\n" + "=" * 60)
        print("  FALHA — backup no D: falhou (atualização BLOQUEADA)")
        print("=" * 60)
        return 1

    print("\n" + "=" * 60)
    print("  BACKUP OK — pode prosseguir com a atualização")
    print("=" * 60)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
