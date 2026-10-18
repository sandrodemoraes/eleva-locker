from repositories.base_repository import BaseRepository


class SiteRepository:

    @staticmethod
    def listar():

        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT s.*,
                    (SELECT COUNT(*) FROM armarios a WHERE a.site_id = s.id) AS total_armarios,
                    (SELECT COUNT(*) FROM empresas e WHERE e.site_id = s.id) AS total_empresas
                FROM sites s
                ORDER BY s.nome
            """).fetchall()

    @staticmethod
    def listar_ativos():

        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT id, nome, codigo
                FROM sites
                WHERE status = 1
                ORDER BY nome
            """).fetchall()

    @staticmethod
    def buscar_por_id(site_id):

        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM sites WHERE id = ?
            """, (site_id,)).fetchone()

    @staticmethod
    def buscar_por_codigo(codigo):

        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM sites WHERE codigo = ?
            """, (codigo,)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO sites (nome, codigo, endereco, cidade, estado, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados["codigo"],
                dados.get("endereco"),
                dados.get("cidade"),
                dados.get("estado"),
                dados.get("status", 1),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def atualizar(site_id, dados):

        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE sites
                SET nome = ?, codigo = ?, endereco = ?, cidade = ?,
                    estado = ?, status = ?
                WHERE id = ?
            """, (
                dados["nome"],
                dados["codigo"],
                dados.get("endereco"),
                dados.get("cidade"),
                dados.get("estado"),
                dados.get("status", 1),
                site_id,
            ))
            conn.commit()

    @staticmethod
    def excluir(site_id):

        with BaseRepository.get_connection() as conn:
            conn.execute("DELETE FROM sites WHERE id = ?", (site_id,))
            conn.commit()
