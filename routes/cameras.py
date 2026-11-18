"""Eleva Cam — site público de câmeras ao vivo + gestão no painel."""

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify,
)

from services.camera_service import CameraService, STREAM_STATUS
from services.clima_service import buscar_clima

cameras_bp = Blueprint("cameras", __name__)


def _clima_da_camera(camera):
    """sqlite3.Row não tem .get(); clima nunca derruba a página."""
    if not camera:
        return None
    try:
        lat = camera["latitude"]
        lon = camera["longitude"]
    except (KeyError, IndexError, TypeError):
        return None
    try:
        return buscar_clima(lat, lon)
    except Exception:
        return None


def _exige_login_html():
    if "usuario" not in session:
        return redirect("/")
    return None


def _exige_login_json():
    if "usuario" not in session:
        return jsonify({
            "sucesso": False,
            "mensagem": "Sessão expirada.",
        }), 401
    return None


def _dados_formulario():
    return {
        "nome": request.form.get("nome", ""),
        "slug": request.form.get("slug", ""),
        "local": request.form.get("local", ""),
        "cidade": request.form.get("cidade", ""),
        "estado": request.form.get("estado", ""),
        "descricao": request.form.get("descricao", ""),
        "youtube_video_id": request.form.get("youtube_video_id", ""),
        "youtube_channel_url": request.form.get("youtube_channel_url", ""),
        "stream_status": request.form.get("stream_status", "offline"),
        "latitude": request.form.get("latitude", ""),
        "longitude": request.form.get("longitude", ""),
        "ordem": request.form.get("ordem", "0"),
        "status": request.form.get("status", "1"),
    }


# ==========================
# SITE PÚBLICO — ELEVA CAM
# ==========================

@cameras_bp.route("/eleva-cam", strict_slashes=False)
@cameras_bp.route("/cameras/ao-vivo")
def eleva_cam_home():
    cameras = CameraService.listar(apenas_ativas=True)
    destaque = cameras[0] if cameras else None

    return render_template(
        "eleva_cam/home.html",
        cameras=cameras,
        destaque=destaque,
        clima=_clima_da_camera(destaque),
    )


@cameras_bp.route("/eleva-cam/<slug>")
def eleva_cam_camera(slug):
    camera = CameraService.buscar_por_slug(slug)

    if not camera:
        return render_template(
            "eleva_cam/home.html",
            cameras=CameraService.listar(apenas_ativas=True),
            destaque=None,
            erro="Câmera não encontrada ou indisponível.",
        ), 404

    outras = [
        item for item in CameraService.listar(apenas_ativas=True)
        if item["id"] != camera["id"]
    ]

    return render_template(
        "eleva_cam/camera.html",
        camera=camera,
        outras=outras,
        clima=_clima_da_camera(camera),
    )


# ==========================
# PAINEL — LISTAR
# ==========================

@cameras_bp.route("/cameras")
def cameras_admin():
    bloqueio = _exige_login_html()
    if bloqueio:
        return bloqueio

    return render_template(
        "cameras.html",
        usuario=session["usuario"],
        perfil=session.get("perfil"),
        cameras=CameraService.listar(),
        stream_status=STREAM_STATUS,
    )


# ==========================
# PAINEL — NOVA
# ==========================

@cameras_bp.route("/cameras/nova", methods=["POST"])
def nova_camera():
    bloqueio = _exige_login_json()
    if bloqueio:
        return bloqueio

    try:
        CameraService.inserir(_dados_formulario())
    except ValueError as erro:
        return jsonify({
            "sucesso": False,
            "mensagem": str(erro),
        })

    return jsonify({
        "sucesso": True,
        "mensagem": "Câmera cadastrada com sucesso.",
    })


# ==========================
# PAINEL — EDITAR
# ==========================

@cameras_bp.route("/cameras/editar/<int:camera_id>", methods=["POST"])
def editar_camera(camera_id):
    bloqueio = _exige_login_html()
    if bloqueio:
        return bloqueio

    if not CameraService.buscar_por_id(camera_id):
        return redirect("/cameras")

    try:
        CameraService.atualizar(camera_id, _dados_formulario())
    except ValueError:
        return redirect("/cameras")

    return redirect("/cameras")


# ==========================
# PAINEL — EXCLUIR
# ==========================

@cameras_bp.route("/cameras/excluir/<int:camera_id>", methods=["POST"])
def excluir_camera(camera_id):
    bloqueio = _exige_login_html()
    if bloqueio:
        return bloqueio

    CameraService.excluir(camera_id)
    return redirect("/cameras")
