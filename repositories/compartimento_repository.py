from repositories.base_repository import BaseRepository


class CompartimentoRepository:

    @staticmethod
    def listar(armario_id=None):

        with BaseRepository.get_connection() as conn:

            if armario_id:

                return conn.execute("""
                    SELECT
                        c.*,
                        a.nome AS armario_nome
                    FROM compartimentos c
                    JOIN armarios a ON a.id = c.armario
                    WHERE c.armario = ?
                    ORDER BY c.numero
                """, (armario_id,)).fetchall()

            return conn.execute("""
                SELECT
                    c.*,
                    a.nome AS armario_nome
                FROM compartimentos c
                JOIN armarios a ON a.id = c.armario
                ORDER BY a.nome, c.numero
            """).fetchall()

    @staticmethod
    def buscar_por_id(compartimento_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    c.*,
                    a.nome AS armario_nome
                FROM compartimentos c
                JOIN armarios a ON a.id = c.armario
                WHERE c.id = ?
            """, (compartimento_id,)).fetchone()

    @staticmethod
    def listar_livres(armario_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id, numero
                FROM compartimentos
                WHERE armario = ? AND status = 'livre'
                ORDER BY numero
            """, (armario_id,)).fetchall()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO compartimentos (
                    armario, numero, rele, esp32_id, status, tamanho, gpio
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["armario"],
                dados["numero"],
                dados.get("rele"),
                dados.get("esp32_id"),
                dados.get("status", "livre"),
                dados.get("tamanho", "M"),
                dados.get("gpio"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(compartimento_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE compartimentos
                SET
                    armario = ?,
                    numero = ?,
                    rele = ?,
                    esp32_id = ?,
                    status = ?,
                    tamanho = ?,
                    gpio = ?
                WHERE id = ?
            """, (
                dados["armario"],
                dados["numero"],
                dados.get("rele"),
                dados.get("esp32_id"),
                dados["status"],
                dados.get("tamanho", "M"),
                dados.get("gpio"),
                compartimento_id,
            ))

            conn.commit()

    @staticmethod
    def atualizar_status(compartimento_id, status):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE compartimentos
                SET status = ?
                WHERE id = ?
            """, (status, compartimento_id))

            conn.commit()

    @staticmethod
    def remover_acima_porta(armario_id, esp32_id, max_portas):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM compartimentos
                WHERE armario = ?
                  AND esp32_id = ?
                  AND numero > ?
                  AND status = 'livre'
            """, (armario_id, esp32_id, max_portas))
            removidos = cursor.rowcount
            conn.commit()
            return removidos

    @staticmethod
    def excluir(compartimento_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                DELETE FROM compartimentos
                WHERE id = ?
            """, (compartimento_id,))

            conn.commit()

    @staticmethod
    def contar(site_id=None):

        with BaseRepository.get_connection() as conn:

            if site_id is not None:
                return conn.execute("""
                    SELECT COUNT(*) AS total
                    FROM compartimentos c
                    JOIN armarios a ON a.id = c.armario
                    WHERE a.site_id = ?
                """, (site_id,)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total FROM compartimentos
            """).fetchone()["total"]

    @staticmethod
    def buscar_por_armario_numero(armario_id, numero):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM compartimentos
                WHERE armario = ? AND numero = ?
            """, (armario_id, numero)).fetchone()

    @staticmethod
    def numero_existe(armario_id, numero, excluir_id=None):

        with BaseRepository.get_connection() as conn:

            if excluir_id:

                row = conn.execute("""
                    SELECT id FROM compartimentos
                    WHERE armario = ? AND numero = ? AND id != ?
                """, (armario_id, numero, excluir_id)).fetchone()

            else:

                row = conn.execute("""
                    SELECT id FROM compartimentos
                    WHERE armario = ? AND numero = ?
                """, (armario_id, numero)).fetchone()

            return row is not None
