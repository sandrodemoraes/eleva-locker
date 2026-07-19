import hashlib
import os

EXCLUIR = {
    "__pycache__",
    ".git",
    "backups",
    ".idea",
    ".vscode"
}

EXTENSOES = (
    ".py",
    ".html",
    ".css",
    ".js",
    ".json",
    ".db",
    ".md"
)


class HashService:

    @staticmethod
    def gerar_hash(projeto):

        sha = hashlib.sha256()

        for raiz, dirs, arquivos in os.walk(projeto):

            dirs[:] = [d for d in dirs if d not in EXCLUIR]

            arquivos.sort()

            for arquivo in arquivos:

                if not arquivo.endswith(EXTENSOES):
                    continue

                caminho = os.path.join(raiz, arquivo)

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