from datetime import datetime

import config
from repositories.lgpd_consentimento_repository import LgpdConsentimentoRepository
from repositories.usuario_repository import UsuarioRepository


class LgpdConsentimentoService:

    @staticmethod
    def consentimento_usuario_ativo():
        return config.LGPD_CONSENTIMENTO_USUARIO

    @staticmethod
    def aviso_totem_ativo():
        return config.LGPD_AVISO_TOTEM

    @staticmethod
    def _agora():
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    @staticmethod
    def registrar(
        titular_tipo,
        finalidade,
        titular_id=None,
        telefone=None,
        email=None,
        ip=None,
        user_agent=None,
    ):
        return LgpdConsentimentoRepository.criar({
            "titular_tipo": titular_tipo,
            "titular_id": titular_id,
            "telefone": telefone,
            "email": email,
            "finalidade": finalidade,
            "versao_politica": config.LGPD_POLITICA_VERSAO,
            "ip": ip,
            "user_agent": user_agent,
            "criado_em": LgpdConsentimentoService._agora(),
        })

    @staticmethod
    def registrar_usuario(usuario_id, email, telefone, ip=None, user_agent=None):
        agora = LgpdConsentimentoService._agora()
        UsuarioRepository.atualizar_consentimento(
            usuario_id,
            versao=config.LGPD_POLITICA_VERSAO,
            ip=ip,
            consentimento_em=agora,
        )
        return LgpdConsentimentoService.registrar(
            titular_tipo="usuario",
            titular_id=usuario_id,
            telefone=telefone,
            email=email,
            finalidade="cadastro_usuario",
            ip=ip,
            user_agent=user_agent,
        )

    @staticmethod
    def registrar_totem_deposito(
        encomenda_id,
        cliente,
        telefone=None,
        email=None,
        usuario_id=None,
        ip=None,
        user_agent=None,
    ):
        return LgpdConsentimentoService.registrar(
            titular_tipo="encomenda",
            titular_id=encomenda_id,
            telefone=telefone,
            email=email,
            finalidade="deposito_totem",
            ip=ip,
            user_agent=user_agent,
        )
