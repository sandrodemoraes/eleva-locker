from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    flash
)

from services.usuario_service import UsuarioService

usuarios_bp = Blueprint("usuarios", __name__)


@usuarios_bp.route("/usuarios")
def usuarios():

    if "usuario" not in session:
        return redirect("/")

    lista = UsuarioService.listar()

    return render_template(
        "usuarios.html",
        usuario=session["usuario"],
        perfil=session["perfil"],
        usuarios=lista
    )


@usuarios_bp.route("/usuarios/novo", methods=["POST"])
def novo_usuario():

    if "usuario" not in session:
        return redirect("/")

    try:

        UsuarioService.criar(
            nome=request.form["nome"],
            email=request.form["email"],
            telefone=request.form["telefone"],
            senha=request.form["senha"],
            confirmar=request.form["confirmar"],
            perfil=request.form["perfil"],
            status=int(request.form["status"])
        )

        flash("Usuário cadastrado com sucesso!", "success")

    except ValueError as erro:

        flash(str(erro), "warning")

    except Exception:

        flash("Erro interno ao cadastrar usuário.", "danger")

    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/editar/<int:usuario_id>", methods=["POST"])
def editar_usuario(usuario_id):

    if "usuario" not in session:
        return redirect("/")

    try:

        UsuarioService.atualizar(
            usuario_id=usuario_id,
            nome=request.form["nome"],
            email=request.form["email"],
            telefone=request.form["telefone"],
            perfil=request.form["perfil"],
            status=int(request.form["status"])
        )

        flash("Usuário atualizado com sucesso!", "success")

    except ValueError as erro:

        flash(str(erro), "warning")

    except Exception:

        flash("Erro interno ao atualizar o usuário.", "danger")

    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/excluir/<int:usuario_id>", methods=["POST"])
def excluir_usuario(usuario_id):

    if "usuario" not in session:
        return redirect("/")

    try:

        UsuarioService.excluir(usuario_id)

        flash("Usuário excluído com sucesso!", "success")

    except ValueError as erro:

        flash(str(erro), "warning")

    except Exception:

        flash("Erro interno ao excluir o usuário.", "danger")

    return redirect("/usuarios")


@usuarios_bp.route("/usuarios/senha/<int:usuario_id>", methods=["POST"])
def alterar_senha(usuario_id):

    if "usuario" not in session:
        return redirect("/")

    try:

        UsuarioService.alterar_senha(
            usuario_id=usuario_id,
            senha=request.form["senha"],
            confirmar=request.form["confirmar"]
        )

        flash("Senha alterada com sucesso!", "success")

    except ValueError as erro:

        flash(str(erro), "warning")

    except Exception:

        flash("Erro interno ao alterar a senha.", "danger")

    return redirect("/usuarios")