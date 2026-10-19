"""Site público — Energia Solar (portfólio + pedido de orçamento) e lista no painel."""

from flask import (
    Blueprint, render_template, request, session, redirect, url_for, flash
)

import config
from middleware.auth_required import login_required
from services.orcamento_solar_service import OrcamentoSolarService, TIPOS_IMOVEL

orcamento_solar_bp = Blueprint("orcamento_solar", __name__)


def _ip_origem():
    xff = request.headers.get("X-Forwarded-For", "")
    if xff:
        return xff.split(",")[0].strip()
    return request.remote_addr


@orcamento_solar_bp.route("/energia-solar", strict_slashes=False)
@orcamento_solar_bp.route("/solar")
def energia_solar():
    return render_template(
        "site/energia_solar.html",
        tipos_imovel=TIPOS_IMOVEL,
        form={},
        erro=None,
        enviado=False,
        protocolo=None,
        contato_telefone=config.ORCAMENTO_SOLAR_WHATSAPP or config.TOTEM_AJUDA_TELEFONE or "",
    )


@orcamento_solar_bp.route("/energia-solar/solicitar", methods=["POST"])
def solicitar():
    dados = {
        "nome": request.form.get("nome", ""),
        "telefone": request.form.get("telefone", ""),
        "email": request.form.get("email", ""),
        "cidade": request.form.get("cidade", ""),
        "estado": request.form.get("estado", ""),
        "tipo_imovel": request.form.get("tipo_imovel", ""),
        "valor_conta": request.form.get("valor_conta", ""),
        "consumo_kwh": request.form.get("consumo_kwh", ""),
        "concessionaria": request.form.get("concessionaria", ""),
        "mensagem": request.form.get("mensagem", ""),
        "lgpd_consentimento": request.form.get("lgpd_consentimento") == "1",
    }

    try:
        resultado = OrcamentoSolarService.solicitar(dados, ip_origem=_ip_origem())
    except ValueError as erro:
        return render_template(
            "site/energia_solar.html",
            tipos_imovel=TIPOS_IMOVEL,
            form=dados,
            erro=str(erro),
            enviado=False,
            protocolo=None,
            contato_telefone=config.ORCAMENTO_SOLAR_WHATSAPP or config.TOTEM_AJUDA_TELEFONE or "",
        )

    return render_template(
        "site/energia_solar.html",
        tipos_imovel=TIPOS_IMOVEL,
        form={},
        erro=None,
        enviado=True,
        protocolo=resultado["id"],
        contato_telefone=config.ORCAMENTO_SOLAR_WHATSAPP or config.TOTEM_AJUDA_TELEFONE or "",
    )


@orcamento_solar_bp.route("/orcamentos-solar")
@login_required
def admin_listar():
    return render_template(
        "site/orcamentos_admin.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        orcamentos=OrcamentoSolarService.listar(),
        novos=OrcamentoSolarService.contar_novos(),
    )


@orcamento_solar_bp.route("/orcamentos-solar/<int:orcamento_id>/atendido", methods=["POST"])
@login_required
def admin_atendido(orcamento_id):
    try:
        OrcamentoSolarService.marcar_atendido(
            orcamento_id,
            session.get("usuario") or session.get("nome") or "admin",
        )
        flash("Orçamento marcado como atendido.", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    return redirect(url_for("orcamento_solar.admin_listar"))
