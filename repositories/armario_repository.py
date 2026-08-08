from repositories.base_repository import BaseRepository


class ArmarioRepository:

    @staticmethod
    def listar(site_id=None):

        with BaseRepository.get_connection() as conn:

            filtro = ""
            params = ()

            if site_id is not None:
                filtro = " WHERE a.site_id = ?"
                params = (site_id,)

            return conn.execute(f"""
                SELECT
                    a.*,
                    e.razao_social AS empresa_nome,
                    s.nome AS site_nome,
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
                LEFT JOIN sites s ON s.id = a.site_id
                {filtro}
                ORDER BY a.nome
            """, params).fetchall()

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
                    nome, endereco, cidade, estado, status, empresa_id, site_id, max_portas
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados["endereco"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
                dados.get("empresa_id"),
                dados.get("site_id"),
                dados.get("max_portas", 16),
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
                    empresa_id = ?,
                    site_id = ?,
                    max_portas = ?
                WHERE id = ?
            """, (
                dados["nome"],
                dados["endereco"],
                dados["cidade"],
                dados["estado"],
                dados["status"],
                dados.get("empresa_id"),
                dados.get("site_id"),
                dados.get("max_portas", 16),
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
    def contar(site_id=None):

        with BaseRepository.get_connection() as conn:

            if site_id is not None:
                return conn.execute("""
                    SELECT COUNT(*) AS total FROM armarios WHERE site_id = ?
                """, (site_id,)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total FROM armarios
            """).fetchone()["total"]
