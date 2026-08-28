"""Rate limit simples em memória (totem público)."""

import time
from functools import wraps

from flask import jsonify, request

_buckets = {}


def rate_limit(key_prefix, max_tentativas=8, janela_seg=300):
    """
    Limita tentativas por IP.
    max_tentativas=8 em 5 min — protege brute-force de código 6 dígitos.
    """

    def decorator(f):

        @wraps(f)
        def wrapped(*args, **kwargs):
            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()
            chave = f"{key_prefix}:{ip}"
            agora = time.time()

            historico = _buckets.get(chave, [])
            historico = [t for t in historico if agora - t < janela_seg]

            if len(historico) >= max_tentativas:
                restante = int(janela_seg - (agora - historico[0]))
                return jsonify({
                    "sucesso": False,
                    "mensagem": f"Muitas tentativas. Aguarde {max(1, restante // 60)} min.",
                }), 429

            historico.append(agora)
            _buckets[chave] = historico
            return f(*args, **kwargs)

        return wrapped

    return decorator


def rate_limit_form(key_prefix, max_tentativas=10, janela_seg=900, template="login.html"):
    """Rate limit para formulários HTML (ex.: login admin)."""

    def decorator(f):

        @wraps(f)
        def wrapped(*args, **kwargs):
            from flask import render_template

            ip = request.headers.get("X-Forwarded-For", request.remote_addr or "unknown")
            if ip and "," in ip:
                ip = ip.split(",")[0].strip()
            chave = f"{key_prefix}:{ip}"
            agora = time.time()

            historico = _buckets.get(chave, [])
            historico = [t for t in historico if agora - t < janela_seg]

            if len(historico) >= max_tentativas:
                restante = int(janela_seg - (agora - historico[0]))
                minutos = max(1, restante // 60)
                return render_template(
                    template,
                    erro=f"Muitas tentativas de login. Aguarde {minutos} min e tente novamente.",
                )

            historico.append(agora)
            _buckets[chave] = historico
            return f(*args, **kwargs)

        return wrapped

    return decorator
