from functools import wraps

from flask import request, jsonify

import config


def esp32_token_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        token = request.headers.get("X-ESP32-Token") or request.args.get("token")

        if not token:
            return jsonify({"sucesso": False, "mensagem": "Token não informado."}), 401

        from services.esp32_service import Esp32Service

        esp = Esp32Service.buscar_por_token(token)

        if not esp:
            return jsonify({"sucesso": False, "mensagem": "Token inválido."}), 403

        request.esp32 = esp

        return f(*args, **kwargs)

    return decorated
