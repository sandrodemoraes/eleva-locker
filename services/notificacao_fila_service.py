"""Fila de reenvio — ajuda totem e encomendas pendentes quando o servidor/WhatsApp volta."""

import config
from services.notificacao_service import NotificacaoService
from services.totem_ajuda_service import TotemAjudaService


class NotificacaoFilaService:

    @staticmethod
    def _whatsapp_disponivel():
        if not config.NOTIF_WHATSAPP_ATIVO:
            return True
        if config.NOTIF_MODO == "console":
            return True
        status = NotificacaoService.status_whatsapp()
        return bool(status.get("pronto"))

    @staticmethod
    def processar():
        """Tenta reenviar ajuda totem e notificações de encomenda pendentes."""
        if not config.NOTIF_FILA_ATIVA:
            return {"ativo": False, "motivo": "NOTIF_FILA_ATIVA=0"}

        if not NotificacaoFilaService._whatsapp_disponivel():
            return {
                "ativo": True,
                "whatsapp_pronto": False,
                "ajuda": {"tentados": 0, "enviados": 0},
                "encomendas": {"tentados": 0, "enviados": 0},
            }

        ajuda = TotemAjudaService.reenviar_whatsapp_pendentes()
        encomendas = NotificacaoService.reenviar_encomendas_pendentes()

        total_enviados = ajuda.get("enviados", 0) + encomendas.get("enviados", 0)
        if total_enviados:
            print(
                f"📬 Fila notificações: {ajuda.get('enviados', 0)} ajuda totem, "
                f"{encomendas.get('enviados', 0)} encomenda(s) reenviada(s)."
            )

        return {
            "ativo": True,
            "whatsapp_pronto": True,
            "ajuda": ajuda,
            "encomendas": encomendas,
        }
