from repositories.base_repository import BaseRepository


class ArmarioRepository:

    @staticmethod
    def listar():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    a.*,
                    e.razao_social AS empresa_nome,
                    (
                        SELECT COUNT(*)
                        FROM compartimentos c
                        WHERE c.armario = a.id
                    ) AS total_compartimentos,
                    (
                        SELECT COUNT(*)
                        FROM compartimentos c
                        WHERE c.armario = a.id AND c.status = 'ocupado'
                    ) AS compartimentos_ocupados
                FROM armarios a
                LEFT JOIN empresas e ON e.id = a.empresa_id
                ORDER BY a.nome
            """).fetchall()

    @staticmethod
    def buscar_por_id(armario_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    a.*,
                    e.razao_social AS empresa_nome
                FROM armarios a
                LEFT JOIN empresas e ON e.id = a.empresa_id
                WHERE a.id = ?
            """, (armario_id,)).fetchone()

    @staticmethod
    def listar_ativos():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id, nome
                FROM armarios
                WHERE status = 'ativo'
                ORDER BY nome
            """).fetchall()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO armarios (
                    nome, endereco, cidade, estado, status, empresa_id
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados["endereco"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
                dados.get("empresa_id"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(armario_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE armarios
                SET
                    nome = ?,
                    endereco = ?,
                    cidade = ?,
                    estado = ?,
                    status = ?,
                    empresa_id = ?
                WHERE id = ?
            """, (
                dados["nome"],
                dados["endereco"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
                dados.get("empresa_id"),
                armario_id,
            ))

            conn.commit()

    @staticmethod
    def excluir(armario_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                DELETE FROM armarios
                WHERE id = ?
            """, (armario_id,))

            conn.commit()

    @staticmethod
    def contar():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total FROM armarios
            """).fetchone()["total"]
