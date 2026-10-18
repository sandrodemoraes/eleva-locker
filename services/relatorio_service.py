from datetime import datetime, timedelta

from repositories.base_repository import BaseRepository


class RelatorioService:
    """BI e previsão simples de ocupação (regressão linear)."""

    @staticmethod
    def _row(row):
        return dict(row) if row else row

    @staticmethod
    def _rows(rows):
        return [dict(r) for r in rows]

    @staticmethod
    def _site_join_armario(alias="a"):
        from middleware.site_scope import clausula_site
        frag, params = clausula_site("site_id", alias)
        return frag, params

    @staticmethod
    def ocupacao_por_armario():

        frag, params = RelatorioService._site_join_armario("a")

        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT
                    a.id,
                    a.nome,
                    COUNT(c.id) AS total,
                    SUM(CASE WHEN c.status = 'ocupado' THEN 1 ELSE 0 END) AS ocupados
                FROM armarios a
                LEFT JOIN compartimentos c ON c.armario = a.id
                WHERE 1=1 {frag}
                GROUP BY a.id, a.nome
                ORDER BY a.nome
            """, params).fetchall()

    @staticmethod
    def encomendas_por_dia(dias=30):

        frag, params = RelatorioService._site_join_armario("a")
        inicio = (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d")

        with BaseRepository.get_connection() as conn:
            rows = conn.execute(f"""
                SELECT
                    substr(e.data_entrada, 1, 10) AS dia,
                    COUNT(*) AS total
                FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                JOIN armarios a ON a.id = c.armario
                WHERE e.data_entrada >= ? {frag}
                GROUP BY substr(e.data_entrada, 1, 10)
                ORDER BY dia
            """, (inicio, *params)).fetchall()

        return rows

    @staticmethod
    def resumo_geral():

        frag, params = RelatorioService._site_join_armario("a")

        with BaseRepository.get_connection() as conn:

            armarios = conn.execute(f"""
                SELECT COUNT(*) AS total FROM armarios a WHERE 1=1 {frag}
            """, params).fetchone()["total"]

            comp = conn.execute(f"""
                SELECT
                    COUNT(c.id) AS total,
                    SUM(CASE WHEN c.status = 'ocupado' THEN 1 ELSE 0 END) AS ocupados
                FROM compartimentos c
                JOIN armarios a ON a.id = c.armario
                WHERE 1=1 {frag}
            """, params).fetchone()

            enc_mes = conn.execute(f"""
                SELECT COUNT(*) AS total
                FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                JOIN armarios a ON a.id = c.armario
                WHERE substr(e.data_entrada, 1, 7) = ?
                {frag}
            """, (
                datetime.now().strftime("%Y-%m"),
                *params,
            )).fetchone()["total"]

        total_comp = comp["total"] or 0
        ocupados = comp["ocupados"] or 0
        taxa = round((ocupados / total_comp * 100), 1) if total_comp else 0

        return {
            "armarios": armarios,
            "compartimentos": total_comp,
            "ocupados": ocupados,
            "taxa_ocupacao": taxa,
            "encomendas_mes": enc_mes,
        }

    @staticmethod
    def previsao_ocupacao(dias_futuros=7):

        """Previsão linear baseada nos últimos 14 dias de encomendas."""
        historico = RelatorioService.encomendas_por_dia(14)

        if len(historico) < 2:
            resumo = RelatorioService.resumo_geral()
            taxa_atual = resumo["taxa_ocupacao"]
            return {
                "metodo": "baseline",
                "taxa_atual": taxa_atual,
                "previsao": [
                    {"dia": (datetime.now() + timedelta(days=i + 1)).strftime("%Y-%m-%d"),
                     "taxa_estimada": taxa_atual}
                    for i in range(dias_futuros)
                ],
            }

        valores = [r["total"] for r in historico]
        n = len(valores)
        xs = list(range(n))
        media_x = sum(xs) / n
        media_y = sum(valores) / n

        num = sum((xs[i] - media_x) * (valores[i] - media_y) for i in range(n))
        den = sum((x - media_x) ** 2 for x in xs) or 1
        slope = num / den
        intercept = media_y - slope * media_x

        resumo = RelatorioService.resumo_geral()
        taxa_base = resumo["taxa_ocupacao"]
        media_diaria = media_y or 1

        previsao = []

        for i in range(1, dias_futuros + 1):
            dia = (datetime.now() + timedelta(days=i)).strftime("%Y-%m-%d")
            enc_est = max(0, intercept + slope * (n + i - 1))
            fator = enc_est / media_diaria if media_diaria else 1
            taxa_est = min(100, round(taxa_base * fator, 1))
            previsao.append({"dia": dia, "taxa_estimada": taxa_est, "encomendas_est": round(enc_est, 1)})

        return {
            "metodo": "regressao_linear",
            "taxa_atual": taxa_base,
            "tendencia_diaria": round(slope, 2),
            "previsao": previsao,
        }

    @staticmethod
    def dados_completos():
        return {
            "resumo": RelatorioService.resumo_geral(),
            "ocupacao_armarios": RelatorioService._rows(
                RelatorioService.ocupacao_por_armario()
            ),
            "encomendas_diarias": RelatorioService._rows(
                RelatorioService.encomendas_por_dia(30)
            ),
            "previsao": RelatorioService.previsao_ocupacao(7),
        }
