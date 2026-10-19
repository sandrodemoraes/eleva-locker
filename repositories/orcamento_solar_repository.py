from datetime import datetime

from repositories.base_repository import BaseRepository


class OrcamentoSolarRepository:
    """Leads de orçamento de energia solar vindos do site público."""

    @staticmethod
    def criar(dados):
        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO orcamentos_solar (
                    nome, telefone, email, cidade, estado, tipo_imovel,
                    valor_conta, consumo_kwh, concessionaria, mensagem,
                    origem, status, notificado, lgpd_consentimento_em,
                    ip_origem, criado_em
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados.get("nome"),
                dados.get("telefone"),
                dados.get("email"),
                dados.get("cidade"),
                dados.get("estado"),
                dados.get("tipo_imovel"),
                dados.get("valor_conta"),
                dados.get("consumo_kwh"),
                dados.get("concessionaria"),
                dados.get("mensagem"),
                dados.get("origem", "site"),
                dados.get("status", "novo"),
                1 if dados.get("notificado") else 0,
                dados.get("lgpd_consentimento_em"),
                dados.get("ip_origem"),
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ))
            conn.commit()
            return cursor.lastrowid

    @staticmethod
    def buscar_por_id(orcamento_id):
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT * FROM orcamentos_solar WHERE id = ?
            """, (orcamento_id,)).fetchone()

    @staticmethod
    def listar(status=None, limite=100):
        params = []
        filtro = ""
        if status:
            filtro = "WHERE status = ?"
            params.append(status)
        params.append(limite)
        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT * FROM orcamentos_solar
                {filtro}
                ORDER BY id DESC
                LIMIT ?
            """, params).fetchall()

    @staticmethod
    def contar_novos():
        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS n FROM orcamentos_solar WHERE status = 'novo'
            """).fetchone()
            return row["n"] if row else 0

    @staticmethod
    def marcar_notificado(orcamento_id, notificado=True):
        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE orcamentos_solar SET notificado = ? WHERE id = ?
            """, (1 if notificado else 0, orcamento_id))
            conn.commit()

    @staticmethod
    def marcar_atendido(orcamento_id, usuario):
        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE orcamentos_solar
                SET status = 'atendido', atendido_em = ?, atendido_por = ?
                WHERE id = ?
            """, (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                usuario,
                orcamento_id,
            ))
            conn.commit()
            row = conn.execute(
                "SELECT status FROM orcamentos_solar WHERE id = ?",
                (orcamento_id,),
            ).fetchone()
            return row is not None and row["status"] == "atendido"
