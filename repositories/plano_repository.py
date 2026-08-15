from repositories.base_repository import BaseRepository


class PlanoRepository:

    @staticmethod
    def listar():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT * FROM planos
                WHERE status = 1
                ORDER BY preco_mensal
            """).fetchall()

    @staticmethod
    def listar_todos():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT * FROM planos ORDER BY preco_mensal
            """).fetchall()

    @staticmethod
    def buscar_por_id(plano_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT * FROM planos WHERE id = ?
            """, (plano_id,)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO planos (
                    nome, descricao, preco_mensal,
                    max_armarios, max_compartimentos, max_encomendas_mes,
                    inclui_whatsapp, inclui_relatorios, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"], dados.get("descricao"), dados["preco_mensal"],
                dados.get("max_armarios", -1), dados.get("max_compartimentos", -1),
                dados.get("max_encomendas_mes", -1),
                dados.get("inclui_whatsapp", 0), dados.get("inclui_relatorios", 1),
                dados.get("status", 1),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(plano_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE planos SET
                    nome=?, descricao=?, preco_mensal=?,
                    max_armarios=?, max_compartimentos=?, max_encomendas_mes=?,
                    inclui_whatsapp=?, inclui_relatorios=?, status=?
                WHERE id=?
            """, (
                dados["nome"], dados.get("descricao"), dados["preco_mensal"],
                dados.get("max_armarios", -1), dados.get("max_compartimentos", -1),
                dados.get("max_encomendas_mes", -1),
                dados.get("inclui_whatsapp", 0), dados.get("inclui_relatorios", 1),
                dados.get("status", 1), plano_id,
            ))

            conn.commit()

    @staticmethod
    def excluir(plano_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("UPDATE planos SET status = 0 WHERE id = ?", (plano_id,))
            conn.commit()
