"""Orçamento de energia solar — recebe leads do site público, grava e notifica.

Regra de ouro: uma falha de notificação (ex.: WhatsApp/Evolution fora do ar)
NUNCA pode impedir de gravar o lead. Primeiro salva, depois tenta avisar.
"""

import re
from datetime import datetime

import config
from repositories.orcamento_solar_repository import OrcamentoSolarRepository
from repositories.notificacao_repository import NotificacaoRepository
from services.notificacao_service import NotificacaoService

TIPOS_IMOVEL = ["Residencial", "Comercial", "Rural", "Industrial"]


class OrcamentoSolarService:

    @staticmethod
    def _num_ou_none(valor):
        if valor is None:
            return None
        txt = str(valor).strip()
        if not txt:
            return None
        txt = txt.replace("R$", "").replace(".", "").replace(",", ".")
        txt = re.sub(r"[^0-9.]", "", txt)
        try:
            return float(txt) if txt else None
        except ValueError:
            return None

    @staticmethod
    def validar(dados):
        erros = []
        nome = (dados.get("nome") or "").strip()
        telefone = (dados.get("telefone") or "").strip()

        if len(nome) < 3:
            erros.append("Informe seu nome completo.")

        numero, erro_tel = NotificacaoService.validar_telefone_br(telefone)
        if erro_tel:
            erros.append(f"WhatsApp/telefone: {erro_tel}")

        tipo = (dados.get("tipo_imovel") or "").strip()
        if tipo and tipo not in TIPOS_IMOVEL:
            erros.append("Tipo de imóvel inválido.")

        return erros, numero

    @staticmethod
    def _montar_msg_interna(orcamento_id, dados):
        linhas = [
            "☀️ *ELEVA — Novo pedido de orçamento solar*",
            f"🧾 Protocolo *#{orcamento_id}*",
            "",
            f"👤 {dados.get('nome')}",
            f"📱 {dados.get('telefone')}",
        ]
        if dados.get("email"):
            linhas.append(f"✉️ {dados['email']}")
        local = " / ".join([p for p in [dados.get("cidade"), dados.get("estado")] if p])
        if local:
            linhas.append(f"📍 {local}")
        if dados.get("tipo_imovel"):
            linhas.append(f"🏠 {dados['tipo_imovel']}")
        if dados.get("valor_conta"):
            linhas.append(f"💡 Conta média: R$ {dados['valor_conta']:.2f}")
        if dados.get("consumo_kwh"):
            linhas.append(f"⚡ Consumo: {dados['consumo_kwh']:.0f} kWh/mês")
        if dados.get("concessionaria"):
            linhas.append(f"🔌 {dados['concessionaria']}")
        if dados.get("mensagem"):
            linhas.append("")
            linhas.append(f"📝 {dados['mensagem']}")
        return "\n".join(linhas)

    @staticmethod
    def _montar_msg_cliente(nome, orcamento_id):
        primeiro = (nome or "").split(" ")[0] if nome else ""
        return (
            f"Olá *{primeiro}*! ☀️\n\n"
            "Recebemos seu pedido de *orçamento de energia solar* na ELEVA.\n"
            f"Protocolo: *#{orcamento_id}*.\n\n"
            "Em breve entramos em contato com sua simulação. Obrigado!"
        )

    @staticmethod
    def _notificar(orcamento_id, dados, telefone_cliente):
        """Best-effort: nunca lança exceção para não travar o lead."""
        houve_ok = False

        # 1) Aviso interno (para o dono do negócio) por WhatsApp
        try:
            destino_interno = (config.ORCAMENTO_SOLAR_WHATSAPP or "").strip()
            if destino_interno:
                msg = OrcamentoSolarService._montar_msg_interna(orcamento_id, dados)
                r = NotificacaoService._enviar_whatsapp(destino_interno, msg)
                ok = bool(r.get("sucesso"))
                houve_ok = houve_ok or (ok and not r.get("simulado"))
                NotificacaoRepository.registrar(
                    None, "orcamento_solar", destino_interno, msg,
                    "enviado" if ok else "erro",
                    r.get("detalhe") or r.get("mensagem"),
                )
        except Exception as erro:
            NotificacaoRepository.registrar(
                None, "orcamento_solar", config.ORCAMENTO_SOLAR_WHATSAPP or "-",
                "(aviso interno)", "erro", str(erro),
            )

        # 2) Aviso interno por e-mail (se configurado)
        try:
            if config.ORCAMENTO_SOLAR_EMAIL:
                assunto = f"Novo orçamento solar #{orcamento_id} — {dados.get('nome')}"
                corpo = OrcamentoSolarService._montar_msg_interna(orcamento_id, dados)
                NotificacaoService._enviar_email(config.ORCAMENTO_SOLAR_EMAIL, assunto, corpo)
        except Exception:
            pass

        # 3) Confirmação para o próprio cliente (opcional)
        try:
            if config.ORCAMENTO_SOLAR_CONFIRMA_CLIENTE and telefone_cliente:
                msg_cli = OrcamentoSolarService._montar_msg_cliente(dados.get("nome"), orcamento_id)
                NotificacaoService._enviar_whatsapp(telefone_cliente, msg_cli)
        except Exception:
            pass

        return houve_ok

    @staticmethod
    def solicitar(dados, ip_origem=None):
        erros, numero = OrcamentoSolarService.validar(dados)
        if erros:
            raise ValueError(" ".join(erros))

        registro = {
            "nome": (dados.get("nome") or "").strip(),
            "telefone": numero or (dados.get("telefone") or "").strip(),
            "email": (dados.get("email") or "").strip() or None,
            "cidade": (dados.get("cidade") or "").strip() or None,
            "estado": (dados.get("estado") or "").strip() or None,
            "tipo_imovel": (dados.get("tipo_imovel") or "").strip() or None,
            "valor_conta": OrcamentoSolarService._num_ou_none(dados.get("valor_conta")),
            "consumo_kwh": OrcamentoSolarService._num_ou_none(dados.get("consumo_kwh")),
            "concessionaria": (dados.get("concessionaria") or "").strip() or None,
            "mensagem": (dados.get("mensagem") or "").strip() or None,
            "origem": dados.get("origem", "site"),
            "ip_origem": ip_origem,
        }
        if dados.get("lgpd_consentimento"):
            registro["lgpd_consentimento_em"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 1) SEMPRE grava primeiro
        orcamento_id = OrcamentoSolarRepository.criar(registro)

        # 2) Depois tenta notificar (sem travar)
        notificado = OrcamentoSolarService._notificar(orcamento_id, registro, numero)
        if notificado:
            OrcamentoSolarRepository.marcar_notificado(orcamento_id, True)

        return {"id": orcamento_id, "notificado": notificado}

    @staticmethod
    def listar(status=None, limite=100):
        return OrcamentoSolarRepository.listar(status=status, limite=limite)

    @staticmethod
    def contar_novos():
        return OrcamentoSolarRepository.contar_novos()

    @staticmethod
    def marcar_atendido(orcamento_id, usuario):
        orc = OrcamentoSolarRepository.buscar_por_id(orcamento_id)
        if not orc:
            raise ValueError("Orçamento não encontrado.")
        if orc["status"] == "atendido":
            raise ValueError("Este orçamento já foi atendido.")
        if not OrcamentoSolarRepository.marcar_atendido(orcamento_id, usuario):
            raise ValueError("Não foi possível marcar como atendido.")
        return True
