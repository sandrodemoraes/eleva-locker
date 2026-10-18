from datetime import datetime

from repositories.base_repository import BaseRepository


class LgpdSolicitacaoRepository:

    @staticmethod
    def criar(tipo, titular_tipo, titular_id, operador, detalhe=None):
        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO lgpd_solicitacoes (
                    tipo, titular_tipo, titular_id, operador, detalhe, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                tipo,
                titular_tipo,
                titular_id,
                operador,
                detalhe,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def listar(limite=50):
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT *
                FROM lgpd_solicitacoes
                ORDER BY id DESC
                LIMIT ?
            """, (limite,)).fetchall()

    @staticmethod
    def listar_por_titular(titular_tipo, titular_id, limite=20):
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT *
                FROM lgpd_solicitacoes
                WHERE titular_tipo = ? AND titular_id = ?
                ORDER BY id DESC
                LIMIT ?
            """, (titular_tipo, titular_id, limite)).fetchall()
