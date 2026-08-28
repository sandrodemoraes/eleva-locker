from flask import Blueprint, render_template, request, jsonify, redirect

import config
from services.encomenda_service import EncomendaService
from services.armario_service import ArmarioService
from services.destinatario_service import DestinatarioService
from services.qrcode_service import QrcodeService

totem_bp = Blueprint("totem", __name__)


@totem_bp.route("/totem")
@totem_bp.route("/totem/<int:armario_id>")
def index(armario_id=None):

    if armario_id is None and config.TOTEM_ARMARIO_ID:
        return redirect(f"/totem/{config.TOTEM_ARMARIO_ID}")

    armarios = ArmarioService.listar_ativos()

    if armario_id is None and len(armarios) == 1:
        return redirect(f"/totem/{armarios[0]['id']}")

    armario = None

    if armario_id:
        try:
            armario = ArmarioService.buscar_por_id(armario_id)
        except ValueError:
            armario = None

    return render_template(
        "totem.html",
        armario=armario,
        armarios=armarios if not armario else None,
        armario_id=armario_id,
    )


@totem_bp.route("/totem/retirar", methods=["POST"])
def retirar():

    codigo = request.form.get("codigo", "").strip()

    try:

        resultado = EncomendaService.retirar(codigo, operador="Totem")

        return jsonify({
            "sucesso": True,
            "mensagem": f"Retirada confirmada! Compartimento #{resultado['compartimento']}",
            "cliente": resultado["cliente"],
            "compartimento": resultado["compartimento"],
            "armario": resultado["armario"],
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400

    except Exception:

        return jsonify({"sucesso": False, "mensagem": "Erro interno."}), 500


@totem_bp.route("/totem/scan", methods=["POST"])
def scan_qrcode():

    dados = request.get_json(silent=True) or {}
    conteudo = dados.get("conteudo", "")

    parsed = QrcodeService.parse_conteudo(conteudo)

    if not parsed:

        return jsonify({"sucesso": False, "mensagem": "QR Code inválido."}), 400

    try:

        resultado = EncomendaService.retirar(parsed["codigo"], operador="Totem-QR")

        return jsonify({
            "sucesso": True,
            "mensagem": f"Retirada confirmada! Compartimento #{resultado['compartimento']}",
            "cliente": resultado["cliente"],
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400


@totem_bp.route("/totem/destinatarios")
def destinatarios_totem():

    termo = request.args.get("q", "").strip()
    armario_raw = request.args.get("armario_id", "").strip()
    armario_id = int(armario_raw) if armario_raw.isdigit() else None

    return jsonify(DestinatarioService.buscar(termo, armario_id))
