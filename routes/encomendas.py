from flask import Blueprint, render_template, request, redirect, session, flash, jsonify, send_file

from middleware.auth_required import login_required
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.compartimento_service import CompartimentoService
from services.notificacao_service import NotificacaoService
from services.qrcode_service import QrcodeService

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

        canais = ", ".join(n["canal"] for n in resultado.get("notificacoes", []))

        flash(
            f"Encomenda depositada! Código: {resultado['codigo']}"
            + (f" — Notificação: {canais}" if canais else ""),
            "success",
        )

        session["ultimo_codigo"] = resultado["codigo"]
        session["ultimo_encomenda_id"] = resultado["id"]

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


@encomendas_bp.route("/encomendas/qrcode/<int:encomenda_id>")
@login_required
def qrcode(encomenda_id):

    encomenda = EncomendaService.buscar_por_id(encomenda_id)

    png = QrcodeService.gerar_png(
        encomenda["codigo"],
        encomenda["armario_nome"],
    )

    return send_file(
        png,
        mimetype="image/png",
        download_name=f"qrcode_{encomenda['codigo']}.png",
    )


@encomendas_bp.route("/encomendas/reenviar/<int:encomenda_id>", methods=["POST"])
@login_required
def reenviar_notificacao(encomenda_id):

    try:

        NotificacaoService.reenviar(encomenda_id)
        flash("Notificação reenviada com sucesso!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao reenviar notificação.", "danger")

    return redirect("/encomendas")
