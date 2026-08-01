from datetime import datetime

from repositories.base_repository import BaseRepository


class LogService:

    @staticmethod
    def registrar(compartimento_id, usuario, acao):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                INSERT INTO logs (compartimento, usuario, data, acao)
                VALUES (?, ?, ?, ?)
            """, (
                compartimento_id,
                usuario,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                acao,
            ))

            conn.commit()

    @staticmethod
    def listar(limite=100):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    l.id,
                    l.compartimento,
                    l.usuario,
                    l.data,
                    l.acao,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM logs l
                LEFT JOIN compartimentos c ON c.id = l.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                ORDER BY l.id DESC
                LIMIT ?
            """, (limite,)).fetchall()
