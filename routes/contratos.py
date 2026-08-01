from flask import Blueprint, render_template, request, redirect, session, flash

from middleware.auth_required import login_required, perfil_required
from services.contrato_service import ContratoService
from services.empresa_service import EmpresaService
from services.plano_service import PlanoService

contratos_bp = Blueprint("contratos", __name__)


@contratos_bp.route("/contratos")
@login_required
@perfil_required("Administrador")
def listar():

    return render_template(
        "contratos.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        contratos=ContratoService.listar(),
        empresas=EmpresaService.listar_ativas(),
        planos=PlanoService.listar(),
    )


@contratos_bp.route("/contratos/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def novo():

    try:

        ContratoService.criar({
            "empresa_id": int(request.form.get("empresa_id")),
            "plano_id": int(request.form.get("plano_id")),
            "data_inicio": request.form.get("data_inicio"),
            "data_fim": request.form.get("data_fim") or None,
            "valor_mensal": request.form.get("valor_mensal") or None,
            "renovacao_automatica": 1 if request.form.get("renovacao_automatica") else 0,
        })

        flash("Contrato criado e primeira fatura gerada!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")

    return redirect("/contratos")


@contratos_bp.route("/contratos/suspender/<int:contrato_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def suspender(contrato_id):

    ContratoService.suspender(contrato_id)
    flash("Contrato suspenso.", "warning")

    return redirect("/contratos")


@contratos_bp.route("/contratos/reativar/<int:contrato_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def reativar(contrato_id):

    ContratoService.reativar(contrato_id)
    flash("Contrato reativado.", "success")

    return redirect("/contratos")


@contratos_bp.route("/contratos/cancelar/<int:contrato_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def cancelar(contrato_id):

    ContratoService.cancelar(contrato_id)
    flash("Contrato cancelado.", "success")

    return redirect("/contratos")
