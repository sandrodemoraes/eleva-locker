from flask import Blueprint, render_template, request, redirect, session, flash, jsonify

from middleware.auth_required import login_required, perfil_required
from services.esp32_service import Esp32Service
from services.armario_service import ArmarioService
from services.backup.backup_service import BackupService
import config

esp32_bp = Blueprint("esp32", __name__)


@esp32_bp.route("/esp32")
@login_required
def listar():

    return render_template(
        "esp32.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        dispositivos=Esp32Service.listar(),
        armarios=ArmarioService.listar_ativos(),
    )


@esp32_bp.route("/esp32/novo", methods=["POST"])
@login_required
@perfil_required("Administrador")
def novo():

    try:

        armario = request.form.get("armario")

        Esp32Service.criar({
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": int(armario) if armario else None,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": int(request.form.get("max_portas", 16)),
            "status": "offline",
        })

        flash("ESP32 cadastrado com sucesso!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao cadastrar ESP32.", "danger")

    return redirect("/esp32")


@esp32_bp.route("/esp32/editar/<int:esp32_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def editar(esp32_id):

    try:

        armario = request.form.get("armario")

        Esp32Service.atualizar(esp32_id, {
            "nome": request.form.get("nome", ""),
            "ip": request.form.get("ip", ""),
            "mac": request.form.get("mac", ""),
            "armario": int(armario) if armario else None,
            "porta": int(request.form.get("porta", 80)),
            "max_portas": int(request.form.get("max_portas", 16)),
            "status": request.form.get("status", "offline"),
            "token": request.form.get("token", ""),
        })

        flash("ESP32 atualizado!", "success")

    except (ValueError, TypeError) as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao atualizar ESP32.", "danger")

    return redirect("/esp32")


@esp32_bp.route("/esp32/excluir/<int:esp32_id>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def excluir(esp32_id):

    try:

        Esp32Service.excluir(esp32_id)
        flash("ESP32 excluído!", "success")

    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao excluir ESP32.", "danger")

    return redirect("/esp32")


@esp32_bp.route("/esp32/testar/<int:esp32_id>", methods=["POST"])
@login_required
def testar(esp32_id):

    resultado = Esp32Service.testar_conexao(esp32_id)

    if resultado.get("sucesso"):
        flash("ESP32 respondeu com sucesso!", "success")
    else:
        flash(f"Falha na conexão: {resultado.get('mensagem')}", "warning")

    return redirect("/esp32")


@esp32_bp.route("/esp32/abrir/<int:compartimento_id>", methods=["POST"])
@login_required
def abrir_compartimento(compartimento_id):

    resultado = Esp32Service.abrir_compartimento(
        compartimento_id,
        operador=session.get("usuario"),
    )

    if resultado["sucesso"]:
        flash(resultado["mensagem"], "success")
    else:
        flash(resultado["mensagem"], "warning")

    return redirect(request.referrer or "/compartimentos")


@esp32_bp.route("/configuracoes")
@login_required
@perfil_required("Administrador")
def configuracoes():

    return render_template(
        "configuracoes.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        backups=BackupService.listar(),
        config=config,
    )


@esp32_bp.route("/configuracoes/backup", methods=["POST"])
@login_required
@perfil_required("Administrador")
def criar_backup():

    ok = BackupService.criar_backup(forcar=True)

    if ok:
        flash("Backup criado com sucesso!", "success")
    else:
        flash("Erro ao criar backup.", "danger")

    return redirect("/configuracoes")


@esp32_bp.route("/configuracoes/restaurar/<int:numero>", methods=["POST"])
@login_required
@perfil_required("Administrador")
def restaurar_backup(numero):

    try:

        BackupService.restaurar(numero)
        flash(f"Backup #{numero} restaurado! Reinicie o servidor se necessário.", "success")

    except FileNotFoundError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao restaurar backup.", "danger")

    return redirect("/configuracoes")
