from flask import Blueprint, render_template, request, redirect, session, flash, jsonify

from middleware.auth_required import login_required
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.compartimento_service import CompartimentoService

encomendas_bp = Blueprint("encomendas", __name__)


@encomendas_bp.route("/encomendas")
@login_required
def listar():

    status = request.args.get("status")

    return render_template(
        "encomendas.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        encomendas=EncomendaService.listar(status),
        armarios=ArmarioService.listar_ativos(),
        status_filtro=status,
    )


@encomendas_bp.route("/encomendas/compartimentos-livres/<int:armario_id>")
@login_required
def compartimentos_livres(armario_id):

    livres = CompartimentoService.listar_livres(armario_id)

    return jsonify([
        {"id": c["id"], "numero": c["numero"]}
        for c in livres
    ])


@encomendas_bp.route("/encomendas/depositar", methods=["POST"])
@login_required
def depositar():

    try:

        resultado = EncomendaService.depositar(
            compartimento_id=int(request.form.get("compartimento_id")),
            cliente=request.form.get("cliente", ""),
            telefone=request.form.get("telefone", ""),
            email=request.form.get("email", ""),
            operador=session.get("usuario"),
            transportadora=request.form.get("transportadora", ""),
            observacao=request.form.get("observacao", ""),
        )

        flash(
            f"Encomenda depositada! Código de retirada: {resultado['codigo']}",
            "success",
        )

        session["ultimo_codigo"] = resultado["codigo"]

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao depositar encomenda.", "danger")

    return redirect("/encomendas")


@encomendas_bp.route("/encomendas/retirar", methods=["POST"])
@login_required
def retirar():

    try:

        resultado = EncomendaService.retirar(
            codigo=request.form.get("codigo", ""),
            operador=session.get("usuario"),
        )

        flash(
            f"Retirada confirmada! {resultado['cliente']} — compartimento {resultado['compartimento']}",
            "success",
        )

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao processar retirada.", "danger")

    return redirect("/encomendas")
