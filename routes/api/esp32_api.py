from flask import Blueprint, request, jsonify

from middleware.esp32_token import esp32_token_required
from services.esp32_service import Esp32Service

esp32_api_bp = Blueprint("esp32_api", __name__, url_prefix="/api/esp32")


@esp32_api_bp.route("/heartbeat", methods=["POST"])
@esp32_token_required
def heartbeat():

    dados = request.get_json(silent=True) or {}

    ip = dados.get("ip") or request.remote_addr
    mac = dados.get("mac")

    try:

        esp32_id = Esp32Service.heartbeat(request.esp32["token"], ip, mac)

        return jsonify({
            "sucesso": True,
            "esp32_id": esp32_id,
            "mensagem": "Heartbeat recebido.",
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400


@esp32_api_bp.route("/evento", methods=["POST"])
@esp32_token_required
def evento():

    dados = request.get_json(silent=True) or {}

    compartimento_id = dados.get("compartimento_id")
    acao = dados.get("acao", "evento")

    if not compartimento_id:

        return jsonify({
            "sucesso": False,
            "mensagem": "compartimento_id é obrigatório.",
        }), 400

    try:

        Esp32Service.registrar_evento(
            request.esp32["token"],
            compartimento_id,
            acao,
        )

        return jsonify({"sucesso": True, "mensagem": "Evento registrado."})

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400


@esp32_api_bp.route("/codigos", methods=["GET"])
@esp32_token_required
def codigos():

    armario_id = request.esp32["armario"]
    codigos = Esp32Service.listar_codigos_ativos(armario_id)

    return jsonify({
        "sucesso": True,
        "codigos": codigos,
    })


@esp32_api_bp.route("/validar-codigo", methods=["POST"])
@esp32_token_required
def validar_codigo():

    dados = request.get_json(silent=True) or {}
    codigo = dados.get("codigo", "").strip()

    if not codigo:

        return jsonify({"sucesso": False, "mensagem": "Código não informado."}), 400

    from services.encomenda_service import EncomendaService

    try:

        resultado = EncomendaService.retirar(codigo, operador=f"ESP32:{request.esp32['nome']}")

        return jsonify({
            "sucesso": True,
            "mensagem": "Retirada confirmada.",
            "encomenda": resultado,
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400
