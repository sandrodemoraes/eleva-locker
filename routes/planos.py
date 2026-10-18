from flask import Blueprint, render_template, request, redirect, session, flash

from middleware.auth_required import login_required, perfil_required
from services.plano_service import PlanoService

planos_bp = Blueprint("planos", __name__)


@planos_bp.route("/planos")
@login_required
@perfil_required("Administrador")
def listar():

    return render_template(
        "planos.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        planos=PlanoService.listar_todos(),
    )


@planos_bp.route("/planos/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def novo():

    try:

        PlanoService.criar({
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "preco_mensal": request.form.get("preco_mensal"),
            "max_armarios": int(request.form.get("max_armarios", -1)),
            "max_compartimentos": int(request.form.get("max_compartimentos", -1)),
            "max_encomendas_mes": int(request.form.get("max_encomendas_mes", -1)),
            "inclui_whatsapp": 1 if request.form.get("inclui_whatsapp") else 0,
            "inclui_relatorios": 1 if request.form.get("inclui_relatorios", "1") else 0,
        })

        flash("Plano criado!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")

    return redirect("/planos")


@planos_bp.route("/planos/editar/<int:plano_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def editar(plano_id):

    try:

        PlanoService.atualizar(plano_id, {
            "nome": request.form.get("nome"),
            "descricao": request.form.get("descricao"),
            "preco_mensal": request.form.get("preco_mensal"),
            "max_armarios": int(request.form.get("max_armarios", -1)),
            "max_compartimentos": int(request.form.get("max_compartimentos", -1)),
            "max_encomendas_mes": int(request.form.get("max_encomendas_mes", -1)),
            "inclui_whatsapp": 1 if request.form.get("inclui_whatsapp") else 0,
            "inclui_relatorios": 1 if request.form.get("inclui_relatorios") else 0,
            "status": int(request.form.get("status", 1)),
        })

        flash("Plano atualizado!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")

    return redirect("/planos")
