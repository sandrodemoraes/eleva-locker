from repositories.base_repository import BaseRepository


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
