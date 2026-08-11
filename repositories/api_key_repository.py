from repositories.base_repository import BaseRepository


class ApiKeyRepository:

    @staticmethod
    def listar(site_id=None):

        with BaseRepository.get_connection() as conn:

            if site_id:
                return conn.execute("""
                    SELECT k.*, s.nome AS site_nome
                    FROM api_keys k
                    LEFT JOIN sites s ON s.id = k.site_id
                    WHERE k.site_id = ?
                    ORDER BY k.nome
                """, (site_id,)).fetchall()

            return conn.execute("""
                SELECT k.*, s.nome AS site_nome
                FROM api_keys k
                LEFT JOIN sites s ON s.id = k.site_id
                ORDER BY k.nome
            """).fetchall()

    @staticmethod
    def buscar_por_chave(chave):

        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM api_keys WHERE chave = ?
            """, (chave,)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO api_keys (site_id, nome, chave, permissoes, ativo)
                VALUES (?, ?, ?, ?, ?)
            """, (
                dados.get("site_id"),
                dados["nome"],
                dados["chave"],
                dados.get("permissoes", "read"),
                dados.get("ativo", 1),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def alternar_ativo(key_id, ativo):

        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE api_keys SET ativo = ? WHERE id = ?
            """, (ativo, key_id))
            conn.commit()

    @staticmethod
    def excluir(key_id):

        with BaseRepository.get_connection() as conn:
            conn.execute("DELETE FROM api_keys WHERE id = ?", (key_id,))
            conn.commit()
