import os
import shutil
from pathlib import Path

from services.backup.hash_service import HashService


class BackupService:

    MAX_BACKUPS = 5

    HASH_FILE = "backups/ultimo.hash"

    @staticmethod
    def criar_backup():

        raiz = Path(__file__).resolve().parents[2]

        hash_atual = HashService.gerar_hash(raiz)

        os.makedirs("backups", exist_ok=True)

        if os.path.exists(BackupService.HASH_FILE):

            with open(BackupService.HASH_FILE, "r") as f:

                ultimo_hash = f.read()

            if ultimo_hash == hash_atual:

                print("✔ Nenhuma alteração. Backup ignorado.")

                return

        BackupService.rotacionar()

        destino = Path("backups") / "backup_01"

        shutil.copytree(
            raiz,
            destino,
            ignore=shutil.ignore_patterns(
                "__pycache__",
                ".git",
                "backups",
                "*.pyc"
            )
        )

        with open(BackupService.HASH_FILE, "w") as f:

            f.write(hash_atual)

        print("✔ Backup criado.")

    @staticmethod
    def rotacionar():

        if os.path.exists("backups/backup_05"):

            shutil.rmtree("backups/backup_05")

        for i in range(4, 0, -1):

            origem = f"backups/backup_{i}"

            destino = f"backups/backup_{i+1}"

            if os.path.exists(origem):

                shutil.move(origem, destino)