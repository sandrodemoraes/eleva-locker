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
    def _raiz():
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def listar():

        backups = []

        for i in range(1, BackupService.MAX_BACKUPS + 1):

            caminho = Path(f"backups/backup_{i:02d}")

            if caminho.exists():

                db = caminho / "database" / "elevalocker.db"
                tamanho = sum(
                    f.stat().st_size
                    for f in caminho.rglob("*")
                    if f.is_file()
                )

                backups.append({
                    "numero": i,
                    "caminho": str(caminho),
                    "tem_banco": db.exists(),
                    "tamanho_kb": round(tamanho / 1024, 1),
                })

        return backups

    @staticmethod
    def criar_backup(forcar=False):

        try:

            raiz = BackupService._raiz()

            os.makedirs("backups", exist_ok=True)

            hash_atual = HashService.gerar_hash(raiz)

            if not forcar and os.path.exists(BackupService.HASH_FILE):

                with open(BackupService.HASH_FILE, "r", encoding="utf-8") as f:
                    ultimo_hash = f.read().strip()

                if ultimo_hash == hash_atual:
                    print("✔ Nenhuma alteração. Backup ignorado.")
                    return False

            BackupService.rotacionar()

            destino = Path("backups") / "backup_01"

            if destino.exists():
                shutil.rmtree(destino)

            for pasta in BackupService.PASTAS:

                origem = raiz / pasta

                if origem.exists():

                    shutil.copytree(
                        origem,
                        destino / pasta,
                        dirs_exist_ok=True
                    )

            for arquivo in BackupService.ARQUIVOS:

                origem = raiz / arquivo

                if origem.exists():

                    destino.mkdir(parents=True, exist_ok=True)

                    shutil.copy2(
                        origem,
                        destino / arquivo
                    )

            with open(BackupService.HASH_FILE, "w", encoding="utf-8") as f:
                f.write(hash_atual)

            print("✔ Backup criado com sucesso.")
            return True

        except Exception as erro:

            print(f"⚠ Erro ao criar backup: {erro}")
            return False

    @staticmethod
    def restaurar(numero=1):

        origem = Path(f"backups/backup_{numero:02d}")

        if not origem.exists():
            raise FileNotFoundError(f"Backup #{numero} não encontrado.")

        raiz = BackupService._raiz()

        for pasta in BackupService.PASTAS:

            origem_pasta = origem / pasta

            if not origem_pasta.exists():
                continue

            destino_pasta = raiz / pasta

            if destino_pasta.exists():
                shutil.rmtree(destino_pasta)

            shutil.copytree(origem_pasta, destino_pasta)

        for arquivo in BackupService.ARQUIVOS:

            origem_arquivo = origem / arquivo

            if origem_arquivo.exists():

                shutil.copy2(origem_arquivo, raiz / arquivo)

        print(f"✔ Backup #{numero} restaurado com sucesso.")
        return True

    @staticmethod
    def rotacionar():

        ultimo = Path(f"backups/backup_{BackupService.MAX_BACKUPS:02d}")

        if ultimo.exists():
            shutil.rmtree(ultimo)

        for i in range(BackupService.MAX_BACKUPS - 1, 0, -1):

            origem = Path(f"backups/backup_{i:02d}")
            destino = Path(f"backups/backup_{i + 1:02d}")

            if origem.exists():

                if destino.exists():
                    shutil.rmtree(destino)

                shutil.move(str(origem), str(destino))
