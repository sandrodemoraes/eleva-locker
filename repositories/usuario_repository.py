from repositories.base_repository import BaseRepository
import re


def _digits_telefone(telefone):
    nums = re.sub(r"\D", "", telefone or "")
    if nums.startswith("55") and len(nums) > 11:
        nums = nums[2:]
    return nums


class UsuarioRepository:

    @staticmethod
    def listar(armario_id=None):

        with BaseRepository.get_connection() as conn:

            if armario_id is not None:
                return conn.execute("""
                    SELECT
                        u.id, u.nome, u.email, u.telefone, u.perfil, u.status,
                        u.ultimo_login, u.armario_id, a.nome AS armario_nome
                    FROM usuarios u
                    LEFT JOIN armarios a ON a.id = u.armario_id
                    WHERE u.armario_id = ?
                    ORDER BY u.nome
                """, (armario_id,)).fetchall()

            return conn.execute("""
                SELECT
                    u.id, u.nome, u.email, u.telefone, u.perfil, u.status,
                    u.ultimo_login, u.armario_id, a.nome AS armario_nome
                FROM usuarios u
                LEFT JOIN armarios a ON a.id = u.armario_id
                ORDER BY u.nome
            """).fetchall()

    @staticmethod
    def buscar_por_id(usuario_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    id, nome, email, telefone, perfil, status,
                    ultimo_login, armario_id
                FROM usuarios
                WHERE id = ?
            """, (usuario_id,)).fetchone()

    @staticmethod
    def buscar_por_email(email):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM usuarios
                WHERE email = ?
            """, (email,)).fetchone()

    @staticmethod
    def buscar_por_telefone(telefone, excluir_id=None):
        alvo = _digits_telefone(telefone)
        if not alvo:
            return None

        with BaseRepository.get_connection() as conn:
            rows = conn.execute("""
                SELECT * FROM usuarios
                WHERE telefone IS NOT NULL AND TRIM(telefone) != ''
            """).fetchall()

        for row in rows:
            if excluir_id and row["id"] == excluir_id:
                continue
            if _digits_telefone(row["telefone"]) == alvo:
                return row
        return None

    @staticmethod
    def buscar_por_nome(nome, excluir_id=None):
        nome = (nome or "").strip()
        if not nome:
            return None

        sql = "SELECT * FROM usuarios WHERE LOWER(TRIM(nome)) = LOWER(?)"
        params = [nome]
        if excluir_id is not None:
            sql += " AND id != ?"
            params.append(excluir_id)

        with BaseRepository.get_connection() as conn:
            return conn.execute(sql, tuple(params)).fetchone()

    @staticmethod
    def criar(nome, email, telefone, senha, perfil, status, armario_id=None):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usuarios
                (nome, email, telefone, senha, perfil, status, armario_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (nome, email, telefone, senha, perfil, status, armario_id))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(usuario_id, nome, email, telefone, perfil, status, armario_id=None):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE usuarios
                SET nome = ?, email = ?, telefone = ?, perfil = ?, status = ?, armario_id = ?
                WHERE id = ?
            """, (nome, email, telefone, perfil, status, armario_id, usuario_id))

            conn.commit()

    @staticmethod
    def alterar_senha(usuario_id, senha_hash):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE usuarios SET senha = ? WHERE id = ?
            """, (senha_hash, usuario_id))

            conn.commit()

    @staticmethod
    def excluir(usuario_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("DELETE FROM usuarios WHERE id = ?", (usuario_id,))

            conn.commit()
