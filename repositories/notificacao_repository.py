from datetime import datetime

from repositories.base_repository import BaseRepository


class NotificacaoRepository:

    @staticmethod
    def registrar(encomenda_id, canal, destinatario, mensagem, status, detalhe=None):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                INSERT INTO notificacoes (
                    encomenda_id, canal, destinatario, mensagem, status, detalhe, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                encomenda_id,
                canal,
                destinatario,
                mensagem,
                status,
                detalhe,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))

            conn.commit()

    @staticmethod
    def listar(limite=100):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    n.*,
                    e.codigo AS encomenda_codigo,
                    e.cliente AS encomenda_cliente
                FROM notificacoes n
                LEFT JOIN encomendas e ON e.id = n.encomenda_id
                ORDER BY n.id DESC
                LIMIT ?
            """, (limite,)).fetchall()

    @staticmethod
    def contar_hoje():

        hoje = datetime.now().strftime("%Y-%m-%d")

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total
                FROM notificacoes
                WHERE criado_em LIKE ?
            """, (f"{hoje}%",)).fetchone()["total"]
