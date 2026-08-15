"""Pedidos de ajuda no totem — alerta portaria (painel + WhatsApp)."""

from datetime import datetime

import config
from repositories.totem_ajuda_repository import TotemAjudaRepository
from repositories.notificacao_repository import NotificacaoRepository
from services.armario_service import ArmarioService
from services.notificacao_service import NotificacaoService


class TotemAjudaService:

    @staticmethod
    def ajuda_habilitada():
        tel = (config.TOTEM_AJUDA_TELEFONE or "").strip()
        return config.TOTEM_AJUDA_ALERTA or bool(tel)

    @staticmethod
    def _nome_armario(armario_id):
        if not armario_id:
            return "Totem (armário não identificado)"
        try:
            arm = ArmarioService.buscar_por_id(armario_id)
            return arm["nome"]
        except ValueError:
            return f"Armário #{armario_id}"

    @staticmethod
    def _montar_mensagem_whatsapp(armario_nome, armario_id=None):
        agora = datetime.now().strftime("%d/%m/%Y %H:%M")
        painel = f"{config.APP_URL_BASE.rstrip('/')}/notificacoes#ajuda-totem"
        totem = NotificacaoService._link_totem(armario_id)
        return (
            f"🆘 *ELEVA LOCKER — Pedido de ajuda*\n\n"
            f"📍 *{armario_nome}*\n"
            f"🕐 {agora}\n\n"
            f"Alguém no totem pediu ajuda (código, porta ou dúvida).\n\n"
            f"👉 Totem: {totem}\n"
            f"👉 Painel: {painel}"
        )

    @staticmethod
    def solicitar(armario_id=None, ip_origem=None):
        if not TotemAjudaService.ajuda_habilitada():
            raise ValueError("Ajuda no totem não está configurada.")

        armario_id_int = int(armario_id) if armario_id else None
        armario_nome = TotemAjudaService._nome_armario(armario_id_int)

        recente = TotemAjudaRepository.ultimo_pendente_armario(armario_id_int)
        if recente:
            return {
                "pedido_id": recente["id"],
                "armario_nome": armario_nome,
                "whatsapp_enviado": bool(recente["whatsapp_enviado"]),
                "duplicado": True,
                "mensagem": "Portaria já foi avisada há instantes. Aguarde ou ligue.",
            }

        mensagem = TotemAjudaService._montar_mensagem_whatsapp(armario_nome, armario_id_int)
        whatsapp_ok = False
        whatsapp_detalhe = ""

        telefone = (config.TOTEM_AJUDA_TELEFONE or "").strip()
        if telefone and config.NOTIF_WHATSAPP_ATIVO:
            resultado = NotificacaoService._enviar_whatsapp(telefone, mensagem)
            whatsapp_ok = bool(resultado.get("sucesso"))
            whatsapp_detalhe = resultado.get("mensagem") or resultado.get("detalhe") or ""
            NotificacaoRepository.registrar(
                None,
                "whatsapp_ajuda",
                telefone,
                mensagem,
                "enviado" if whatsapp_ok else "erro",
                whatsapp_detalhe,
            )
        elif telefone and config.NOTIF_MODO == "console":
            print(f"\n🆘 [AJUDA TOTEM → {telefone}]\n{mensagem}\n")
            whatsapp_ok = True
            whatsapp_detalhe = "Modo console — mensagem no terminal"
            NotificacaoRepository.registrar(
                None,
                "whatsapp_ajuda",
                telefone,
                mensagem,
                "enviado",
                whatsapp_detalhe,
            )

        pedido_id = TotemAjudaRepository.criar({
            "armario_id": armario_id_int,
            "armario_nome": armario_nome,
            "whatsapp_enviado": whatsapp_ok,
            "whatsapp_detalhe": whatsapp_detalhe,
            "ip_origem": ip_origem,
        })

        msg_usuario = "Portaria avisada!"
        if whatsapp_ok:
            msg_usuario += " Você também pode ligar."
        elif telefone:
            msg_usuario = "Registramos seu pedido. Ligue para a portaria."
        else:
            msg_usuario = "Registramos seu pedido. Aguarde a portaria."

        return {
            "pedido_id": pedido_id,
            "armario_nome": armario_nome,
            "whatsapp_enviado": whatsapp_ok,
            "duplicado": False,
            "mensagem": msg_usuario,
        }

    @staticmethod
    def listar(status=None, limite=50):
        return TotemAjudaRepository.listar(status=status, limite=limite)

    @staticmethod
    def contar_pendentes():
        return TotemAjudaRepository.contar_pendentes()

    @staticmethod
    def marcar_atendido(pedido_id, usuario):
        pedido = TotemAjudaRepository.buscar_por_id(pedido_id)
        if not pedido:
            raise ValueError("Pedido de ajuda não encontrado.")
        if pedido["status"] != "pendente":
            raise ValueError("Este pedido já foi atendido.")
        if not TotemAjudaRepository.marcar_atendido(pedido_id, usuario):
            raise ValueError("Não foi possível marcar como atendido.")
        return True
