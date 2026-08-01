from repositories.base_repository import BaseRepository


class EncomendaRepository:

    @staticmethod
    def listar(status=None):

        with BaseRepository.get_connection() as conn:

            if status:

                return conn.execute("""
                    SELECT
                        e.*,
                        c.numero AS compartimento_numero,
                        a.nome AS armario_nome
                    FROM encomendas e
                    LEFT JOIN compartimentos c ON c.id = e.compartimento
                    LEFT JOIN armarios a ON a.id = c.armario
                    WHERE e.status = ?
                    ORDER BY e.id DESC
                """, (status,)).fetchall()

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                ORDER BY e.id DESC
            """).fetchall()

    @staticmethod
    def buscar_por_id(encomenda_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE e.id = ?
            """, (encomenda_id,)).fetchone()

    @staticmethod
    def buscar_por_codigo(codigo):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE e.codigo = ? AND e.status = 'aguardando_retirada'
            """, (codigo,)).fetchone()

    @staticmethod
    def codigo_existe(codigo):

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT id FROM encomendas
                WHERE codigo = ? AND status = 'aguardando_retirada'
            """, (codigo,)).fetchone()

            return row is not None

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO encomendas (
                    codigo, cliente, telefone, email, compartimento,
                    data_entrada, status, operador, transportadora, observacao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["codigo"],
                dados["cliente"],
                dados.get("telefone"),
                dados.get("email"),
                dados["compartimento"],
                dados["data_entrada"],
                dados.get("status", "aguardando_retirada"),
                dados.get("operador"),
                dados.get("transportadora"),
                dados.get("observacao"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar_retirada(encomenda_id, data_retirada):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE encomendas
                SET status = 'retirada', data_retirada = ?
                WHERE id = ?
            """, (data_retirada, encomenda_id))

            conn.commit()

    @staticmethod
    def marcar_notificado(encomenda_id):

        from datetime import datetime

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE encomendas
                SET notificado_em = ?
                WHERE id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                encomenda_id,
            ))

            conn.commit()

    @staticmethod
    def contar(status=None):

        with BaseRepository.get_connection() as conn:

            if status:

                return conn.execute("""
                    SELECT COUNT(*) AS total
                    FROM encomendas
                    WHERE status = ?
                """, (status,)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total FROM encomendas
            """).fetchone()["total"]

    @staticmethod
    def contar_pendentes():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total
                FROM encomendas
                WHERE status = 'aguardando_retirada'
            """).fetchone()["total"]
