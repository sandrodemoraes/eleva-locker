"""Job de retenção LGPD — anonimiza/arquiva dados antigos (Fase 4)."""

from datetime import datetime, timedelta
from pathlib import Path

import config
from repositories.base_repository import BaseRepository
from repositories.lgpd_titular_repository import ANONIMIZADO, LgpdTitularRepository

LOG_PATH = Path(__file__).resolve().parents[1] / "logs" / "lgpd_retencao.log"


class LgpdRetencaoService:

    @staticmethod
    def _cutoff(dias):
        return (datetime.now() - timedelta(days=dias)).strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def _log(linha):
        LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with LOG_PATH.open("a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {linha}\n")

    @staticmethod
    def _encomendas_elegiveis(cutoff):
        with BaseRepository.get_connection() as conn:
            return conn.execute("""
                SELECT id, cliente, data_retirada
                FROM encomendas
                WHERE status = 'retirada'
                  AND data_retirada IS NOT NULL
                  AND data_retirada < ?
                  AND (lgpd_anonimizado_em IS NULL OR lgpd_anonimizado_em = '')
                  AND cliente != ?
            """, (cutoff, ANONIMIZADO)).fetchall()

    @staticmethod
    def _retencao_encomendas(simular):
        cutoff = LgpdRetencaoService._cutoff(config.LGPD_RETENCAO_ENCOMENDA_DIAS)
        rows = LgpdRetencaoService._encomendas_elegiveis(cutoff)
        ids = [r["id"] for r in rows]
        if not simular:
            for eid in ids:
                LgpdTitularRepository.anonimizar_encomenda(eid)
        return {"elegiveis": len(ids), "ids": ids[:20], "cutoff": cutoff}

    @staticmethod
    def _retencao_logs(simular):
        cutoff = LgpdRetencaoService._cutoff(config.LGPD_RETENCAO_LOG_DIAS)
        with BaseRepository.get_connection() as conn:
            row = conn.execute(
                "SELECT COUNT(*) AS n FROM logs WHERE data < ?",
                (cutoff,),
            ).fetchone()
            total = row["n"] if row else 0
            if not simular and total:
                conn.execute("DELETE FROM logs WHERE data < ?", (cutoff,))
                conn.commit()
        return {"elegiveis": total, "cutoff": cutoff}

    @staticmethod
    def _retencao_ajuda_totem(simular):
        cutoff = LgpdRetencaoService._cutoff(config.LGPD_RETENCAO_AJUDA_TOTEM_DIAS)
        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS n
                FROM totem_ajuda_pedidos
                WHERE status = 'atendido'
                  AND atendido_em IS NOT NULL
                  AND atendido_em < ?
                  AND (ip_origem IS NOT NULL AND ip_origem != '')
            """, (cutoff,)).fetchone()
            total = row["n"] if row else 0
            if not simular and total:
                conn.execute("""
                    UPDATE totem_ajuda_pedidos
                    SET ip_origem = NULL,
                        whatsapp_detalhe = COALESCE(whatsapp_detalhe, '') || ' [retencao lgpd]'
                    WHERE status = 'atendido'
                      AND atendido_em IS NOT NULL
                      AND atendido_em < ?
                      AND (ip_origem IS NOT NULL AND ip_origem != '')
                """, (cutoff,))
                conn.commit()
        return {"elegiveis": total, "cutoff": cutoff}

    @staticmethod
    def _retencao_notificacoes(simular):
        cutoff = LgpdRetencaoService._cutoff(config.LGPD_RETENCAO_NOTIFICACAO_DIAS)
        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT COUNT(*) AS n
                FROM notificacoes
                WHERE criado_em < ?
                  AND (destinatario IS NULL OR destinatario != ?)
            """, (cutoff, ANONIMIZADO)).fetchone()
            total = row["n"] if row else 0
            if not simular and total:
                conn.execute("""
                    UPDATE notificacoes
                    SET destinatario = ?,
                        mensagem = '[retencao lgpd]'
                    WHERE criado_em < ?
                      AND (destinatario IS NULL OR destinatario != ?)
                """, (ANONIMIZADO, cutoff, ANONIMIZADO))
                conn.commit()
        return {"elegiveis": total, "cutoff": cutoff}

    @staticmethod
    def executar(simular=True):
        modo = "SIMULACAO" if simular else "EXECUCAO"
        LgpdRetencaoService._log(f"--- Inicio {modo} ---")

        resultado = {
            "modo": modo,
            "encomendas": LgpdRetencaoService._retencao_encomendas(simular),
            "logs": LgpdRetencaoService._retencao_logs(simular),
            "ajuda_totem": LgpdRetencaoService._retencao_ajuda_totem(simular),
            "notificacoes": LgpdRetencaoService._retencao_notificacoes(simular),
        }

        resumo = (
            f"{modo}: encomendas={resultado['encomendas']['elegiveis']} "
            f"logs={resultado['logs']['elegiveis']} "
            f"ajuda={resultado['ajuda_totem']['elegiveis']} "
            f"notif={resultado['notificacoes']['elegiveis']}"
        )
        LgpdRetencaoService._log(resumo)
        return resultado
