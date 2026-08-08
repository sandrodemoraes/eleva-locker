from flask import Blueprint, request, jsonify

from middleware.esp32_token import esp32_token_required
from services.esp32_service import Esp32Service
from services.esp32_sync_service import Esp32SyncService

esp32_api_bp = Blueprint("esp32_api", __name__, url_prefix="/api/esp32")


@esp32_api_bp.route("/sync", methods=["GET"])
@esp32_token_required
def sync():

    try:

        pacote = Esp32SyncService.obter_pacote_sync(request.esp32["id"])

        return jsonify({
            "sucesso": True,
            "sync": pacote,
        })

    except ValueError as erro:

        return jsonify({"sucesso": False, "mensagem": str(erro)}), 400


@esp32_api_bp.route("/eventos", methods=["POST"])
@esp32_token_required
def eventos_batch():

    dados = request.get_json(silent=True) or {}
    eventos = dados.get("eventos", [])

    if not isinstance(eventos, list):

        return jsonify({
            "sucesso": False,
            "mensagem": "Campo 'eventos' deve ser uma lista.",
        }), 400

    resultados = Esp32SyncService.processar_eventos(
        request.esp32["id"],
        eventos,
        esp_nome=request.esp32["nome"],
    )

    return jsonify({
        "sucesso": True,
        "processados": resultados,
    })


@esp32_api_bp.route("/heartbeat", methods=["POST"])
@esp32_token_required
def heartbeat():

    dados = request.get_json(silent=True) or {}

    ip = dados.get("ip") or request.remote_addr
    mac = dados.get("mac")
    versao_local = dados.get("sync_versao")

    try:

        esp32_id = Esp32Service.heartbeat(request.esp32["token"], ip, mac)

        versao_servidor = request.esp32["sync_versao"] or 1

        with __import__(
            "repositories.base_repository", fromlist=["BaseRepository"]
        ).BaseRepository.get_connection() as conn:
            row = conn.execute(
                "SELECT sync_versao FROM esp32 WHERE id = ?",
                (esp32_id,),
            ).fetchone()
            if row:
                versao_servidor = row["sync_versao"] or 1

        precisa_sync = (
            versao_local is None
            or int(versao_local) < int(versao_servidor)
        )

        return jsonify({
            "sucesso": True,
            "esp32_id": esp32_id,
            "mensagem": "Heartbeat recebido.",
            "sync_versao": versao_servidor,
            "precisa_sync": precisa_sync,
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
