from werkzeug.security import generate_password_hash
import sqlite3

import config
from repositories.usuario_repository import UsuarioRepository
from services.lgpd_consentimento_service import LgpdConsentimentoService


class UsuarioService:

    @staticmethod
    def _normalizar_armario_id(perfil, armario_id):
        if armario_id in (None, "", 0, "0"):
            return None
        if perfil in ("Operador", "Usuário"):
            return int(armario_id)
        return None

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
        telefone = telefone.strip()

        if not nome or not email or not senha:
            raise ValueError("Preencha todos os campos obrigatórios.")

        if senha != confirmar:
            raise ValueError("As senhas não conferem.")

        if UsuarioRepository.buscar_por_email(email):
            raise ValueError("Este e-mail já está cadastrado. Use outro e-mail.")

        if config.LGPD_CONSENTIMENTO_USUARIO and not lgpd_consentimento:
            raise ValueError("É necessário aceitar a Política de Privacidade.")

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
        telefone = telefone.strip()

        if not nome or not email:
            raise ValueError("Nome e e-mail são obrigatórios.")

        usuario = UsuarioRepository.buscar_por_id(usuario_id)

        if not usuario:
            raise ValueError("Usuário não encontrado.")

        usuario_email = UsuarioRepository.buscar_por_email(email)

        if usuario_email and usuario_email["id"] != usuario_id:
            raise ValueError("Este e-mail já está cadastrado.")

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
