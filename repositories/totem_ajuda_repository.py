from datetime import datetime, timedelta

from repositories.base_repository import BaseRepository


class TotemAjudaRepository:

    @staticmethod
    def criar(dados):
        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO totem_ajuda_pedidos (
                    armario_id, armario_nome, status, whatsapp_enviado,
                    whatsapp_detalhe, ip_origem, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.get("armario_id"),
                dados.get("armario_nome"),
                dados.get("status", "pendente"),
                1 if dados.get("whatsapp_enviado") else 0,
                dados.get("whatsapp_detalhe"),
                dados.get("ip_origem"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_por_id(pedido_id):
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT *
                FROM totem_ajuda_pedidos
                WHERE id = ?
            """, (pedido_id,)).fetchone()

    @staticmethod
    def ultimo_pendente_armario(armario_id, segundos=120):
        limite = (datetime.now() - timedelta(seconds=segundos)).strftime("%Y-%m-%d %H:%M:%S")
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT *
                FROM totem_ajuda_pedidos
                WHERE status = 'pendente'
                  AND armario_id IS ?
                  AND criado_em >= ?
                ORDER BY id DESC
                LIMIT 1
            """, (armario_id, limite)).fetchone()

    @staticmethod
    def listar(status=None, limite=50):
        params = []
        filtro = ""
        if status:
            filtro = "WHERE status = ?"
            params.append(status)

        params.append(limite)
        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT *
                FROM totem_ajuda_pedidos
                {filtro}
                ORDER BY id DESC
                LIMIT ?
            """, params).fetchall()

    @staticmethod
    def contar_pendentes():
        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS n
                FROM totem_ajuda_pedidos
                WHERE status = 'pendente'
            """).fetchone()
            return row["n"] if row else 0

    @staticmethod
    def marcar_atendido(pedido_id, usuario):
        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE totem_ajuda_pedidos
                SET status = 'atendido',
                    atendido_em = ?,
                    atendido_por = ?
                WHERE id = ? AND status = 'pendente'
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                usuario,
                pedido_id,
            ))
            conn.commit()
            return conn.total_changes > 0

    @staticmethod
    def listar_whatsapp_pendentes(horas=72, limite=30):
        limite_data = (datetime.now() - timedelta(hours=horas)).strftime("%Y-%m-%d %H:%M:%S")
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT *
                FROM totem_ajuda_pedidos
                WHERE status = 'pendente'
                  AND whatsapp_enviado = 0
                  AND criado_em >= ?
                ORDER BY id ASC
                LIMIT ?
            """, (limite_data, limite)).fetchall()

    @staticmethod
    def atualizar_whatsapp(pedido_id, enviado, detalhe=None):
        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE totem_ajuda_pedidos
                SET whatsapp_enviado = ?,
                    whatsapp_detalhe = ?
                WHERE id = ?
            """, (1 if enviado else 0, detalhe, pedido_id))
            conn.commit()
