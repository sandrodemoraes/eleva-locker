from flask import Blueprint, render_template, request, redirect, session
from werkzeug.security import check_password_hash
from database import conectar
from datetime import datetime

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/")
def home():
    return render_template("login.html")


@auth_bp.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    senha = request.form["senha"]

    conn = conectar()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT *
        FROM usuarios
        WHERE email = ?
        """,
        (email,)
    )

    usuario = cursor.fetchone()

    if usuario and check_password_hash(usuario["senha"], senha):

        cursor.execute(
            """
            UPDATE usuarios
            SET ultimo_login = ?
            WHERE id = ?
            """,
            (
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                usuario["id"],
            ),
        )

        conn.commit()
        conn.close()

        session["usuario"] = usuario["nome"]
        session["nome"] = usuario["nome"]
        session["perfil"] = usuario["perfil"]
        session["usuario_id"] = usuario["id"]
        session["armario_id"] = usuario["armario_id"] if usuario["armario_id"] else None
        session["site_id"] = 1

        if usuario["perfil"] == "Operador" and usuario["armario_id"]:
            return redirect(f"/armarios/{usuario['armario_id']}")

        return redirect("/dashboard")

    conn.close()

    return render_template(
        "login.html",
        erro="E-mail ou senha inválidos."
    )


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect("/")