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
    def _enviar_whatsapp_portaria(telefone, mensagem):
        telefone = (telefone or "").strip()
        if not telefone:
            return False, "TOTEM_AJUDA_TELEFONE não configurado no .env"

        if not config.NOTIF_WHATSAPP_ATIVO:
            if config.NOTIF_MODO == "console":
                print(f"\n🆘 [AJUDA TOTEM → {telefone}]\n{mensagem}\n")
                NotificacaoRepository.registrar(
                    None, "whatsapp_ajuda", telefone, mensagem, "enviado",
                    "Modo console — mensagem no terminal",
                )
                return True, "Modo console — veja o terminal do servidor"
            return False, "NOTIF_WHATSAPP_ATIVO=0 no .env"

        if config.NOTIF_MODO == "console":
            print(f"\n🆘 [AJUDA TOTEM → {telefone}]\n{mensagem}\n")
            NotificacaoRepository.registrar(
                None, "whatsapp_ajuda", telefone, mensagem, "enviado",
                "Modo console — mensagem no terminal",
            )
            return True, "Modo console — veja o terminal do servidor"

        status = NotificacaoService.status_whatsapp()
        if not status.get("pronto"):
            msg = status.get("mensagem") or "WhatsApp não está pronto."
            NotificacaoRepository.registrar(
                None, "whatsapp_ajuda", telefone, mensagem, "erro", msg,
            )
            return False, msg

        resultado = NotificacaoService._enviar_whatsapp(telefone, mensagem)
        ok = bool(resultado.get("sucesso"))
        detalhe = resultado.get("mensagem") or resultado.get("detalhe") or ""
        NotificacaoRepository.registrar(
            None,
            "whatsapp_ajuda",
            telefone,
            mensagem,
            "enviado" if ok else "erro",
            detalhe,
        )
        return ok, detalhe if ok else (resultado.get("mensagem") or "Falha ao enviar WhatsApp.")

    @staticmethod
    def solicitar(armario_id=None, ip_origem=None):
        if not TotemAjudaService.ajuda_habilitada():
            raise ValueError("Ajuda no totem não está configurada.")

        armario_id_int = int(armario_id) if armario_id else None
        armario_nome = TotemAjudaService._nome_armario(armario_id_int)
        telefone = (config.TOTEM_AJUDA_TELEFONE or "").strip()
        mensagem = TotemAjudaService._montar_mensagem_whatsapp(armario_nome, armario_id_int)

        recente = TotemAjudaRepository.ultimo_pendente_armario(armario_id_int)
        if recente and recente["whatsapp_enviado"]:
            return {
                "pedido_id": recente["id"],
                "armario_nome": armario_nome,
                "whatsapp_enviado": True,
                "whatsapp_erro": "",
                "duplicado": True,
                "mensagem": "Portaria já foi avisada há instantes. Aguarde ou ligue.",
            }

        if recente and not recente["whatsapp_enviado"]:
            whatsapp_ok, whatsapp_detalhe = TotemAjudaService._enviar_whatsapp_portaria(
                telefone, mensagem,
            )
            TotemAjudaRepository.atualizar_whatsapp(
                recente["id"], whatsapp_ok, whatsapp_detalhe,
            )
            return TotemAjudaService._resposta_pedido(
                recente["id"], armario_nome, whatsapp_ok, whatsapp_detalhe, duplicado=True,
            )

        whatsapp_ok, whatsapp_detalhe = TotemAjudaService._enviar_whatsapp_portaria(
            telefone, mensagem,
        )

        pedido_id = TotemAjudaRepository.criar({
            "armario_id": armario_id_int,
            "armario_nome": armario_nome,
            "whatsapp_enviado": whatsapp_ok,
            "whatsapp_detalhe": whatsapp_detalhe,
            "ip_origem": ip_origem,
        })

        return TotemAjudaService._resposta_pedido(
            pedido_id, armario_nome, whatsapp_ok, whatsapp_detalhe, duplicado=False,
        )

    @staticmethod
    def _resposta_pedido(pedido_id, armario_nome, whatsapp_ok, whatsapp_detalhe, duplicado):
        if whatsapp_ok:
            msg = "Portaria avisada por WhatsApp!"
            if duplicado:
                msg = "WhatsApp reenviado para a portaria."
        elif (config.TOTEM_AJUDA_TELEFONE or "").strip():
            msg = "Pedido registrado. WhatsApp não enviou — ligue para a portaria."
        else:
            msg = "Pedido registrado. Aguarde a portaria."

        return {
            "pedido_id": pedido_id,
            "armario_nome": armario_nome,
            "whatsapp_enviado": whatsapp_ok,
            "whatsapp_erro": "" if whatsapp_ok else (whatsapp_detalhe or "Erro desconhecido"),
            "duplicado": duplicado,
            "mensagem": msg,
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

    @staticmethod
    def diagnosticar():
        tel = (config.TOTEM_AJUDA_TELEFONE or "").strip()
        wa = NotificacaoService.status_whatsapp()
        numero, erro_tel = NotificacaoService.validar_telefone_br(tel) if tel else (None, "Sem telefone")
        return {
            "totem_ajuda_alerta": config.TOTEM_AJUDA_ALERTA,
            "totem_ajuda_telefone": tel,
            "telefone_valido": numero,
            "telefone_erro": erro_tel,
            "notif_modo": config.NOTIF_MODO,
            "whatsapp_ativo": config.NOTIF_WHATSAPP_ATIVO,
            "whatsapp_status": wa,
        }
