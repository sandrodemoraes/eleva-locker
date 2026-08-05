from flask import Blueprint, render_template, request, redirect, session, flash, jsonify, send_file

import config
from middleware.auth_required import login_required
from middleware.operador_scope import get_armario_restrito, operador_acessa_armario, redirect_home
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
    restrito = get_armario_restrito()
    armario_filtro = restrito if restrito else request.args.get("armario_id", type=int)

    return render_template(
        "encomendas.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        encomendas=EncomendaService.listar(status, armario_id=armario_filtro),
        armarios=ArmarioService.listar_ativos(),
        status_filtro=status,
        armario_filtro=armario_filtro,
        operador_restrito=restrito is not None,
        whatsapp_ativo=config.NOTIF_WHATSAPP_ATIVO,
    )


@encomendas_bp.route("/encomendas/compartimentos-livres/<int:armario_id>")
@login_required
def compartimentos_livres(armario_id):

    if not operador_acessa_armario(armario_id):
        return jsonify({"erro": "Sem permissão"}), 403

    livres = CompartimentoService.listar_livres(armario_id)

    return jsonify([
        {
            "id": c["id"],
            "numero": c["numero"],
            "tamanho": c["tamanho"] or "M",
        }
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

        canais = NotificacaoService.formatar_resultado_notificacoes(
            resultado.get("notificacoes", [])
        )

        msg = f"Encomenda depositada! Código: {resultado['codigo']}"
        if canais:
            msg += f" — Notificações: {canais}"

        whatsapp_falhou = any(
            n.get("canal") == "whatsapp" and not n.get("sucesso")
            for n in resultado.get("notificacoes", [])
        )
        whatsapp_simulado = any(
            n.get("canal") == "whatsapp" and n.get("sucesso") and n.get("simulado")
            for n in resultado.get("notificacoes", [])
        )
        if whatsapp_falhou or whatsapp_simulado:
            flash(msg, "warning")
        else:
            flash(msg, "success")

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

    try:
        encomenda = EncomendaService.buscar_por_id(encomenda_id, verificar_acesso=True)
    except ValueError as erro:
        flash(str(erro), "warning")
        return redirect("/encomendas")

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
