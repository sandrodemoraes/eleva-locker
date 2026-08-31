from werkzeug.security import generate_password_hash
import re
import secrets
import sqlite3

import config
from repositories.usuario_repository import UsuarioRepository
from services.lgpd_consentimento_service import LgpdConsentimentoService
from services.notificacao_service import NotificacaoService


class UsuarioService:

    @staticmethod
    def _normalizar_armario_id(perfil, armario_id):
        if armario_id in (None, "", 0, "0"):
            return None
        if perfil in ("Operador", "Usuário"):
            return int(armario_id)
        return None

    @staticmethod
    def _validar_telefone(telefone, obrigatorio=True):
        telefone = (telefone or "").strip()
        if not telefone:
            if obrigatorio:
                raise ValueError("Telefone é obrigatório (WhatsApp do morador).")
            return ""
        _, erro = NotificacaoService.validar_telefone_br(telefone)
        if erro:
            raise ValueError(erro)
        return telefone

    @staticmethod
    def _validar_duplicatas(nome, email, telefone, excluir_id=None):
        existente = UsuarioRepository.buscar_por_email(email)
        if existente and (excluir_id is None or existente["id"] != excluir_id):
            raise ValueError(
                "Este e-mail já está cadastrado. Use outro e-mail ou edite o usuário existente."
            )

        if telefone:
            existente = UsuarioRepository.buscar_por_telefone(telefone, excluir_id=excluir_id)
            if existente:
                raise ValueError(
                    f"Este telefone já está cadastrado para {existente['nome']}. "
                    "Verifique o cadastro ou use outro número."
                )

        existente = UsuarioRepository.buscar_por_nome(nome, excluir_id=excluir_id)
        if existente:
            raise ValueError(
                f"Este nome já está cadastrado (e-mail: {existente['email']}). "
                "Use outro nome ou edite o usuário existente."
            )

    @staticmethod
    def listar(armario_id=None):
        return UsuarioRepository.listar(armario_id)

    @staticmethod
    def buscar_por_id(usuario_id):

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        return usuario

    @staticmethod
    def criar(nome, email, telefone, senha, confirmar, perfil, status, armario_id=None,
              lgpd_consentimento=False, ip=None, user_agent=None):

        nome = nome.strip()
        email = email.strip().lower()
        telefone = UsuarioService._validar_telefone(telefone, obrigatorio=True)

        if not nome or not email or not senha:
            raise ValueError("Preencha nome, e-mail, telefone e senha.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        UsuarioService._validar_duplicatas(nome, email, telefone)

        if config.LGPD_CONSENTIMENTO_USUARIO and not lgpd_consentimento:
            raise ValueError(
                "Marque a caixa de consentimento LGPD (Política de Privacidade) antes de cadastrar."
            )

        armario_id = UsuarioService._normalizar_armario_id(perfil, armario_id)
        senha_hash = generate_password_hash(senha)

        try:
            usuario_id = UsuarioRepository.criar(
                nome, email, telefone, senha_hash, perfil, status, armario_id
            )
            if config.LGPD_CONSENTIMENTO_USUARIO and lgpd_consentimento:
                LgpdConsentimentoService.registrar_usuario(
                    usuario_id, email, telefone, ip=ip, user_agent=user_agent,
                )
            return usuario_id
        except sqlite3.IntegrityError:
            raise ValueError("Este e-mail já está cadastrado. Use outro e-mail.")

    @staticmethod
    def atualizar(usuario_id, nome, email, telefone, perfil, status, armario_id=None):

        nome = nome.strip()
        email = email.strip().lower()
        telefone = UsuarioService._validar_telefone(telefone, obrigatorio=False)

        if not nome or not email:
            raise ValueError("Nome e e-mail são obrigatórios.")

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        UsuarioService._validar_duplicatas(nome, email, telefone, excluir_id=usuario_id)

        armario_id = UsuarioService._normalizar_armario_id(perfil, armario_id)

        UsuarioRepository.atualizar(
            usuario_id, nome, email, telefone, perfil, status, armario_id
        )

    @staticmethod
    def alterar_senha(usuario_id, senha, confirmar):

        if not senha:
            raise ValueError("Informe a nova senha.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        UsuarioRepository.alterar_senha(usuario_id, generate_password_hash(senha))

    @staticmethod
    def excluir(usuario_id):

        if not UsuarioRepository.buscar_por_id(usuario_id):
            raise ValueError("Usuário não encontrado.")

        UsuarioRepository.excluir(usuario_id)

    @staticmethod
    def criar_morador_armario(nome, telefone, armario_id, email=None, senha=None):
        """Cadastro enxuto de morador — só o que o totem precisa (nome + telefone + armário)."""
        nome = (nome or "").strip()
        telefone = UsuarioService._validar_telefone(telefone, obrigatorio=True)
        if not nome:
            raise ValueError("Nome é obrigatório.")

        email = (email or "").strip().lower()
        if not email:
            digits = re.sub(r"\D", "", telefone)
            email = f"morador.{digits}@eleva.local"

        if not senha:
            senha = secrets.token_urlsafe(10)

        lgpd = bool(config.LGPD_CONSENTIMENTO_USUARIO)

        return UsuarioService.criar(
            nome=nome,
            email=email,
            telefone=telefone,
            senha=senha,
            confirmar=senha,
            perfil="Usuário",
            status=1,
            armario_id=armario_id,
            lgpd_consentimento=lgpd,
            ip="127.0.0.1",
            user_agent="cadastro_morador_cli",
        )
