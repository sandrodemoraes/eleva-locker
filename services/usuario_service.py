import sqlite3

DB = "database/elevalocker.db"


class UsuarioService:

    @staticmethod
    def listar():

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        usuarios = conn.execute("""
            SELECT
                id,
                nome,
                email,
                telefone,
                perfil,
                status,
                ultimo_login
            FROM usuarios
            ORDER BY nome
        """).fetchall()

        conn.close()

        return usuarios