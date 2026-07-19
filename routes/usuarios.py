from flask import Blueprint, render_template, request, redirect, session, flash
from werkzeug.security import generate_password_hash

from database import conectar
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

    nome = request.form["nome"].strip()
    email = request.form["email"].strip().lower()
    telefone = request.form["telefone"].strip()
    perfil = request.form["perfil"]
    status = int(request.form["status"])

    senha = request.form["senha"]
    confirmar = request.form["confirmar"]

    if not nome or not email or not senha:
        flash("Preencha todos os campos obrigatórios.")
        return redirect("/usuarios")

    if senha != confirmar:
        flash("As senhas não conferem.")
        return redirect("/usuarios")

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM usuarios WHERE email=?",
        (email,)
    )

    existe = cursor.fetchone()

    if existe:
        conn.close()
        flash("Este e-mail já está cadastrado.")
        return redirect("/usuarios")

    senha_hash = generate_password_hash(senha)

    cursor.execute("""
        INSERT INTO usuarios
        (
            nome,
            email,
            telefone,
            senha,
            perfil,
            status
        )
        VALUES
        (
            ?,?,?,?,?,?
        )
    """,
    (
        nome,
        email,
        telefone,
        senha_hash,
        perfil,
        status
    ))

    conn.commit()
    conn.close()

    flash("Usuário cadastrado com sucesso!")

    return redirect("/usuarios")