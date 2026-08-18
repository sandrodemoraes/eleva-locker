from flask import Blueprint, render_template, request, redirect, session, flash, jsonify

from middleware.auth_required import login_required, perfil_required
from services.esp32_service import Esp32Service
from services.armario_service import ArmarioService
from services.backup.backup_service import BackupService
from services.usuario_service import UsuarioService
from repositories.compartimento_repository import CompartimentoRepository
from repositories.esp32_repository import Esp32Repository
import config

esp32_bp = Blueprint("esp32", __name__)


def _redirect_pos_acao_esp(esp32_id=None, compartimento_id=None, fallback="/armarios"):
    destino = request.form.get("redirect") or request.referrer
    if destino:
        return redirect(destino)

    if esp32_id:
        esp = Esp32Repository.buscar_por_id(esp32_id)
        if esp and esp["armario"]:
            return redirect(f"/armarios/{esp['armario']}")

    if compartimento_id:
        comp = CompartimentoRepository.buscar_por_id(compartimento_id)
        if comp and comp["armario"]:
            return redirect(f"/armarios/{comp['armario']}")

    return redirect(fallback)


@esp32_bp.route("/esp32")
@login_required
def listar():

    flash("Gerencie a placa ESP pelo armário: Armários → abrir o armário desejado.", "info")
    return redirect("/armarios")


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

    return _redirect_pos_acao_esp(esp32_id=esp32_id)


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

    return _redirect_pos_acao_esp(compartimento_id=compartimento_id, fallback="/compartimentos")


@esp32_bp.route("/esp32/bancada")
@login_required
@perfil_required("Administrador")
def bancada():

    dispositivos = Esp32Service.listar()
    compartimentos = CompartimentoRepository.listar()

    bancada_comps = [
        c for c in compartimentos
        if c.get("armario_nome") in ("ELEVA Locker Matriz", "Bancada Teste")
    ]
    if not bancada_comps:
        bancada_comps = [c for c in compartimentos if c.get("esp32_id")]

    return render_template(
        "esp32_bancada.html",
        usuario=session.get("usuario"),
        perfil=session.get("perfil"),
        dispositivos=dispositivos,
        compartimentos=sorted(bancada_comps, key=lambda x: x.get("numero") or 0),
    )


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


@esp32_bp.route("/configuracoes/minha-senha", methods=["POST"])
@login_required
@perfil_required("Administrador")
def minha_senha():

    usuario_id = session.get("usuario_id")
    if not usuario_id:
        flash("Sessão inválida. Faça login novamente.", "warning")
        return redirect("/configuracoes")

    try:
        UsuarioService.alterar_senha(
            usuario_id=usuario_id,
            senha=request.form["senha"],
            confirmar=request.form["confirmar"],
        )
        flash("Sua senha foi alterada com sucesso!", "success")
    except ValueError as erro:
        flash(str(erro), "warning")
    except Exception:
        flash("Erro ao alterar senha.", "danger")

    return redirect("/configuracoes")
