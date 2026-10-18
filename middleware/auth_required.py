from functools import wraps

from flask import redirect, session, flash


def login_required(f):

    @wraps(f)
    def decorated(*args, **kwargs):

        if "usuario_id" not in session:
            return redirect("/")

        return f(*args, **kwargs)

    return decorated


def perfil_required(*perfis):

    def decorator(f):

        @wraps(f)
        def decorated(*args, **kwargs):

            if "usuario_id" not in session:
                return redirect("/")

            if session.get("perfil") not in perfis:
                flash("Você não tem permissão para acessar esta página.", "danger")
                return redirect("/dashboard")

            return f(*args, **kwargs)

        return decorated

    return decorator
