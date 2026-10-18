import hashlib
from pathlib import Path


class HashService:

    PASTAS = [
        "database",
        "uploads",
        "config",
        "logs"
    ]

    ARQUIVOS = [
        "PROJETO.md",
        ".env",
    ]

    @staticmethod
    def gerar_hash(raiz):

        raiz = Path(raiz)

        sha = hashlib.sha256()

        # ==========================
        # Pastas
        # ==========================

        for pasta in HashService.PASTAS:

            caminho = raiz / pasta

            if not caminho.exists():
                continue

            for arquivo in sorted(caminho.rglob("*")):

                if arquivo.is_file():

                    try:

                        with open(arquivo, "rb") as f:

                            while True:

                                bloco = f.read(4096)

                                if not bloco:
                                    break

                                sha.update(bloco)

                    except Exception:
                        pass

        # ==========================
        # Arquivos
        # ==========================

        for arquivo in HashService.ARQUIVOS:

            caminho = raiz / arquivo

            if caminho.exists():

                try:

                    with open(caminho, "rb") as f:

                        while True:

                            bloco = f.read(4096)

                            if not bloco:
                                break

                            sha.update(bloco)

                except Exception:
                    pass

        return sha.hexdigest()