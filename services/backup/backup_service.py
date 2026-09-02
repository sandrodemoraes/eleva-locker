import os
import shutil
from pathlib import Path

import config
from services.backup.hash_service import HashService


class BackupService:

    PASTAS = [
        "database",
        "uploads",
        "config",
        "logs",
    ]

    ARQUIVOS = [
        "PROJETO.md",
        ".env",
    ]

    @staticmethod
    def _raiz():
        return Path(__file__).resolve().parents[2]

    @staticmethod
    def _backup_root():
        caminho = Path(getattr(config, "BACKUP_DIR", "backups"))
        if not caminho.is_absolute():
            caminho = BackupService._raiz() / caminho
        return caminho

    @staticmethod
    def _hash_file():
        return BackupService._backup_root() / "ultimo.hash"

    @staticmethod
    def _destino_backup(numero):
        return BackupService._backup_root() / f"backup_{numero:02d}"

    @staticmethod
    def listar():

        backups = []
        max_backups = config.BACKUP_MAX

        for i in range(1, max_backups + 1):

            caminho = BackupService._destino_backup(i)

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
            root = BackupService._backup_root()

            os.makedirs(root, exist_ok=True)

            hash_atual = HashService.gerar_hash(raiz)
            hash_file = BackupService._hash_file()

            if not forcar and hash_file.exists():

                ultimo_hash = hash_file.read_text(encoding="utf-8").strip()

                if ultimo_hash == hash_atual:
                    print("✔ Nenhuma alteração. Backup ignorado.")
                    return False

            BackupService.rotacionar()

            destino = BackupService._destino_backup(1)

            if destino.exists():
                shutil.rmtree(destino)

            for pasta in BackupService.PASTAS:

                origem = raiz / pasta

                if origem.exists():

                    shutil.copytree(
                        origem,
                        destino / pasta,
                        dirs_exist_ok=True,
                    )

            for arquivo in BackupService.ARQUIVOS:

                origem = raiz / arquivo

                if origem.exists():

                    destino.mkdir(parents=True, exist_ok=True)

                    shutil.copy2(origem, destino / arquivo)

            hash_file.write_text(hash_atual, encoding="utf-8")

            print(f"✔ Backup criado em: {destino}")
            return True

        except Exception as erro:

            print(f"⚠ Erro ao criar backup: {erro}")
            return False

    @staticmethod
    def restaurar(numero=1):

        origem = BackupService._destino_backup(numero)

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

        max_backups = config.BACKUP_MAX
        ultimo = BackupService._destino_backup(max_backups)

        if ultimo.exists():
            shutil.rmtree(ultimo)

        for i in range(max_backups - 1, 0, -1):

            origem = BackupService._destino_backup(i)
            destino = BackupService._destino_backup(i + 1)

            if origem.exists():

                if destino.exists():
                    shutil.rmtree(destino)

                shutil.move(str(origem), str(destino))
