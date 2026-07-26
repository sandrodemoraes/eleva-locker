import os
import shutil
from pathlib import Path

from services.backup.hash_service import HashService


class BackupService:

    MAX_BACKUPS = 5

    HASH_FILE = "backups/ultimo.hash"

    PASTAS = [
        "database",
        "uploads",
        "config",
        "logs"
    ]

    ARQUIVOS = [
        "PROJETO.md"
    ]

    @staticmethod
    def criar_backup():

        try:

            raiz = Path(__file__).resolve().parents[2]

            os.makedirs("backups", exist_ok=True)

            hash_atual = HashService.gerar_hash(raiz)

            if os.path.exists(BackupService.HASH_FILE):

                with open(BackupService.HASH_FILE, "r", encoding="utf-8") as f:
                    ultimo_hash = f.read().strip()

                if ultimo_hash == hash_atual:
                    print("✔ Nenhuma alteração. Backup ignorado.")
                    return

            BackupService.rotacionar()

            destino = Path("backups") / "backup_01"

            if destino.exists():
                shutil.rmtree(destino)

            # Copia somente as pastas necessárias
            for pasta in BackupService.PASTAS:

                origem = raiz / pasta

                if origem.exists():

                    shutil.copytree(
                        origem,
                        destino / pasta,
                        dirs_exist_ok=True
                    )

            # Copia os arquivos importantes
            for arquivo in BackupService.ARQUIVOS:

                origem = raiz / arquivo

                if origem.exists():

                    (destino).mkdir(parents=True, exist_ok=True)

                    shutil.copy2(
                        origem,
                        destino / arquivo
                    )

            with open(BackupService.HASH_FILE, "w", encoding="utf-8") as f:
                f.write(hash_atual)

            print("✔ Backup criado com sucesso.")

        except Exception as erro:

            print(f"⚠ Erro ao criar backup: {erro}")

    @staticmethod
    def rotacionar():

        ultimo = Path(f"backups/backup_{BackupService.MAX_BACKUPS}")

        if ultimo.exists():
            shutil.rmtree(ultimo)

        for i in range(BackupService.MAX_BACKUPS - 1, 0, -1):

            origem = Path(f"backups/backup_{i}")
            destino = Path(f"backups/backup_{i + 1}")

            if origem.exists():

                if destino.exists():
                    shutil.rmtree(destino)

                shutil.move(origem, destino)