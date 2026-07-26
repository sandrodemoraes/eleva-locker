from repositories.base_repository import BaseRepository


class UsuarioRepository:

    @staticmethod
    def listar():
        """
        Retorna todos os usuários ordenados por nome.
        """

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
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

    @staticmethod
    def buscar_por_id(usuario_id):
        """
        Retorna um usuário pelo ID.
        """

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    id,
                    nome,
                    email,
                    telefone,
                    perfil,
                    status,
                    ultimo_login
                FROM usuarios
                WHERE id = ?
            """, (usuario_id,)).fetchone()

    @staticmethod
    def buscar_por_email(email):
        """
        Retorna um usuário pelo e-mail.
        """

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM usuarios
                WHERE email = ?
            """, (email,)).fetchone()

    @staticmethod
    def criar(
        nome,
        email,
        telefone,
        senha,
        perfil,
        status
    ):
        """
        Insere um novo usuário.
        """

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO usuarios
                (
                    nome,
                    email,
                    telefone,
                    senha,
                    perfil,
                    status
                )
                VALUES
                (
                    ?,?,?,?,?,?
                )
            """,
            (
                nome,
                email,
                telefone,
                senha,
                perfil,
                status
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(
        usuario_id,
        nome,
        email,
        telefone,
        perfil,
        status
    ):
        """
        Atualiza os dados de um usuário.
        """

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE usuarios
                SET
                    nome = ?,
                    email = ?,
                    telefone = ?,
                    perfil = ?,
                    status = ?
                WHERE id = ?
            """,
            (
                nome,
                email,
                telefone,
                perfil,
                status,
                usuario_id
            ))

            conn.commit()

    @staticmethod
    def alterar_senha(usuario_id, senha_hash):
        """
        Atualiza a senha do usuário.
        """

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE usuarios
                SET senha = ?
                WHERE id = ?
            """,
            (
                senha_hash,
                usuario_id
            ))

            conn.commit()

    @staticmethod
    def excluir(usuario_id):
        """
        Exclui um usuário.
        """

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                DELETE FROM usuarios
                WHERE id = ?
            """, (usuario_id,))

            conn.commit()