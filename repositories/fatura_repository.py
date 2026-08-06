from repositories.base_repository import BaseRepository


class FaturaRepository:

    @staticmethod
    def listar(status=None, contrato_id=None):

        with BaseRepository.get_connection() as conn:

            query = """
                SELECT
                    f.*,
                    c.empresa_id,
                    e.razao_social AS empresa_nome,
                    p.nome AS plano_nome
                FROM faturas f
                JOIN contratos c ON c.id = f.contrato_id
                JOIN empresas e ON e.id = c.empresa_id
                JOIN planos p ON p.id = c.plano_id
                WHERE 1=1
            """
            params = []

            if status:
                query += " AND f.status = ?"
                params.append(status)

            if contrato_id:
                query += " AND f.contrato_id = ?"
                params.append(contrato_id)

            query += " ORDER BY f.id DESC"

            return conn.execute(query, params).fetchall()

    @staticmethod
    def buscar_por_id(fatura_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    f.*,
                    c.empresa_id, c.plano_id,
                    e.razao_social AS empresa_nome,
                    e.email AS empresa_email,
                    p.nome AS plano_nome
                FROM faturas f
                JOIN contratos c ON c.id = f.contrato_id
                JOIN empresas e ON e.id = c.empresa_id
                JOIN planos p ON p.id = c.plano_id
                WHERE f.id = ?
            """, (fatura_id,)).fetchone()

    @staticmethod
    def buscar_por_referencia(contrato_id, referencia):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id FROM faturas
                WHERE contrato_id = ? AND referencia = ?
            """, (contrato_id, referencia)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO faturas (
                    contrato_id, referencia, valor, status,
                    data_vencimento, link_pagamento, gateway_id
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["contrato_id"], dados["referencia"], dados["valor"],
                dados.get("status", "pendente"), dados.get("data_vencimento"),
                dados.get("link_pagamento"), dados.get("gateway_id"),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def marcar_pago(fatura_id, data_pagamento, gateway_id=None):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE faturas
                SET status = 'pago', data_pagamento = ?, gateway_id = COALESCE(?, gateway_id)
                WHERE id = ?
            """, (data_pagamento, gateway_id, fatura_id))

            conn.commit()

    @staticmethod
    def marcar_vencidas(data_hoje):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE faturas
                SET status = 'vencido'
                WHERE status = 'pendente' AND data_vencimento < ?
            """, (data_hoje,))

            conn.commit()

    @staticmethod
    def buscar_por_gateway(gateway_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT id FROM faturas WHERE gateway_id = ?
            """, (gateway_id,)).fetchone()

    @staticmethod
    def calcular_mrr():

        with BaseRepository.get_connection() as conn:

            row = conn.execute("""
                SELECT COALESCE(SUM(c.valor_mensal), 0) AS mrr
                FROM contratos c
                WHERE c.status = 'ativo'
            """).fetchone()

            return row["mrr"]

    @staticmethod
    def contar_pendentes():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COUNT(*) AS total FROM faturas
                WHERE status IN ('pendente', 'vencido')
            """).fetchone()["total"]

    @staticmethod
    def total_recebido_mes(referencia):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT COALESCE(SUM(valor), 0) AS total
                FROM faturas
                WHERE status = 'pago' AND referencia = ?
            """, (referencia,)).fetchone()["total"]
