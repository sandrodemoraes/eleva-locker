"""Rotas públicas LGPD — Fase 1 (transparência, sem bloqueio operacional)."""

from flask import Blueprint, render_template
import config

lgpd_bp = Blueprint("lgpd", __name__)


def _ctx():
    contato_tel = config.LGPD_CONTATO_TELEFONE or config.TOTEM_AJUDA_TELEFONE or ""
    return {
        "lgpd_versao": config.LGPD_POLITICA_VERSAO,
        "lgpd_controlador": config.LGPD_CONTROLADOR_NOME,
        "lgpd_email": config.LGPD_CONTATO_EMAIL,
        "lgpd_telefone": contato_tel,
        "app_url_base": config.APP_URL_BASE.rstrip("/"),
    }


@lgpd_bp.route("/privacidade")
def privacidade():
    return render_template("lgpd/privacidade.html", **_ctx())


@lgpd_bp.route("/termos")
def termos():
    return render_template("lgpd/termos.html", **_ctx())


@lgpd_bp.route("/lgpd")
def index():
    return render_template("lgpd/index.html", **_ctx())
