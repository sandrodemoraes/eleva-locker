"""Autenticação para depósito no totem (PIN ou login operador)."""

from werkzeug.security import check_password_hash

import config
from repositories.usuario_repository import UsuarioRepository


def autorizar_deposito_totem(dados):
    """
    Retorna nome do operador se autorizado, None se não.
    dados: dict com pin e/ou email+senha
    """
    pin = (dados.get("pin") or "").strip()

    if config.TOTEM_DEPOSITO_PIN and pin == config.TOTEM_DEPOSITO_PIN:
        return "Totem-Portaria"

    email = (dados.get("email") or "").strip()
    senha = dados.get("senha") or ""

    if not email or not senha:
        return None

    usuario = UsuarioRepository.buscar_por_email(email)

    if not usuario or not check_password_hash(usuario["senha"], senha):
        return None

    if usuario["perfil"] not in ("Administrador", "Operador"):
        return None

    if usuario["status"] != 1:
        return None

    return usuario["nome"]


def deposito_totem_habilitado():
    return bool(config.TOTEM_DEPOSITO_PIN) or True  # login operador sempre disponível
