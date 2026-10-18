from flask import Blueprint, render_template, request, redirect, session, flash

from middleware.auth_required import login_required, perfil_required
from services.faturamento_service import FaturamentoService

faturas_bp = Blueprint("faturas", __name__)


@faturas_bp.route("/faturas")
@login_required
@perfil_required("Administrador", "Operador")
def listar():

    status = request.args.get("status")

    return render_template(
        "faturas.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        faturas=FaturamentoService.listar_faturas(status),
        status_filtro=status,
    )


@faturas_bp.route("/faturas/gerar-mes", methods=["POST"])
@login_required
@perfil_required("Administrador")
def gerar_mes():

    geradas = FaturamentoService.gerar_faturas_mes()
    flash(f"{geradas} fatura(s) gerada(s) para o mês atual.", "success")

    return redirect("/faturas")


@faturas_bp.route("/faturas/pagar/<int:fatura_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def marcar_pago(fatura_id):

    try:

        FaturamentoService.marcar_pago(fatura_id)
        flash("Fatura marcada como paga!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")

    return redirect("/faturas")


@faturas_bp.route("/faturas/pagar/<gateway_id>")
def pagar_gateway(gateway_id):

    try:

        FaturamentoService.pagar_por_gateway(gateway_id)

        return render_template(
            "pagamento_ok.html",
            mensagem="Pagamento confirmado! Obrigado.",
        )

    except ValueError as erro:

        return render_template(
            "pagamento_ok.html",
            mensagem=str(erro),
            erro=True,
        )
