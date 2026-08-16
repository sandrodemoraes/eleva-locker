"""Escopo multi-site via sessão Flask."""

from flask import has_request_context, session


def get_site_id():
    """None = todos os sites; int = filtrar por site."""
    if not has_request_context():
        return None
    return session.get("site_id")


def set_site_id(site_id):
    if not has_request_context():
        return
    if site_id in (None, "", "all", "0"):
        session.pop("site_id", None)
    else:
        session["site_id"] = int(site_id)


def clausula_site(coluna="site_id", alias=None):
    """Retorna (sql_fragment, params) para filtrar por site."""
    site_id = get_site_id()
    if site_id is None:
        return "", ()
    col = f"{alias}.{coluna}" if alias else coluna
    return f" AND {col} = ?", (site_id,)
