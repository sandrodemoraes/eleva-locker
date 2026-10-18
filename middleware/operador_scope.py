"""Escopo do operador: todos os armários ou um armário específico."""

from flask import session


def is_admin():
    return session.get("perfil") == "Administrador"


def get_armario_restrito():
    """
    None = sem restrição (admin ou operador de todos os armários).
    int  = operador vinculado a um armário (ex.: síndico do condomínio).
    """
    if is_admin():
        return None
    if session.get("perfil") != "Operador":
        return None
    return session.get("armario_id")


def operador_acessa_armario(armario_id):
    if armario_id is None:
        return True
    if is_admin():
        return True
    if session.get("perfil") != "Operador":
        return True
    restrito = session.get("armario_id")
    if restrito is None:
        return True
    return int(restrito) == int(armario_id)


def redirect_home():
    restrito = get_armario_restrito()
    if restrito:
        return f"/armarios/{restrito}"
    return "/dashboard"


def label_escopo_armario(armario_id, armario_nome=None):
    if armario_id:
        return armario_nome or f"Armário #{armario_id}"
    return "Todos os armários"
