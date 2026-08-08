from functools import wraps

from flask import request, jsonify

from repositories.api_key_repository import ApiKeyRepository


def api_key_required(*permissoes_minimas):
    """Autentica requisições da API pública via header X-API-Key."""

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            chave = request.headers.get("X-API-Key", "").strip()

            if not chave:
                return jsonify({
                    "sucesso": False,
                    "mensagem": "Header X-API-Key é obrigatório.",
                }), 401

            registro = ApiKeyRepository.buscar_por_chave(chave)

            if not registro or not registro["ativo"]:
                return jsonify({
                    "sucesso": False,
                    "mensagem": "Chave de API inválida ou inativa.",
                }), 401

            perm = registro["permissoes"] or "read"

            if permissoes_minimas:
                ordem = {"read": 1, "write": 2, "admin": 3}
                if ordem.get(perm, 0) < max(ordem.get(p, 0) for p in permissoes_minimas):
                    return jsonify({
                        "sucesso": False,
                        "mensagem": "Permissão insuficiente para esta operação.",
                    }), 403

            request.api_key = registro
            return f(*args, **kwargs)

        return decorated

    return decorator
