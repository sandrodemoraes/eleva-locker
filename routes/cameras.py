"""Eleva Cam — site público de câmeras ao vivo + gestão no painel."""

import os
from datetime import datetime, timezone

from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    session,
    jsonify,
    Response,
    url_for,
)

from services.camera_service import CameraService, STREAM_STATUS
from services.clima_service import buscar_clima

cameras_bp = Blueprint("cameras", __name__)

# Base canônica pública do Eleva Cam (SEO / sitemap)
ELEVA_CAM_PUBLIC_BASE = os.getenv(
    "ELEVA_CAM_PUBLIC_BASE",
    "https://elevacam.elevalocker.com.br",
).rstrip("/")


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


def _eleva_cam_url(path="/eleva-cam"):
    if not path.startswith("/"):
        path = "/" + path
    return f"{ELEVA_CAM_PUBLIC_BASE}{path}"


def _eleva_cam_seo(path="/eleva-cam", title=None, description=None):
    return {
        "canonical_url": _eleva_cam_url(path),
        "og_title": title or "Eleva Cam — câmeras ao vivo",
        "og_description": description
        or "Câmeras ao vivo em pontos turísticos. Serra do Rio do Rastro — Lauro Müller/SC.",
        "og_url": _eleva_cam_url(path),
    }


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

@cameras_bp.route("/robots.txt")
def robots_txt():
    corpo = "\n".join(
        [
            "User-agent: *",
            "Allow: /eleva-cam",
            "Allow: /eleva-cam/",
            "Allow: /static/",
            "Disallow: /cameras",
            "Disallow: /login",
            "Disallow: /dashboard",
            "Disallow: /usuarios",
            "Disallow: /empresas",
            "Disallow: /armarios",
            "Disallow: /compartimentos",
            "Disallow: /encomendas",
            "Disallow: /esp32",
            "Disallow: /totem",
            "Disallow: /financeiro",
            "Disallow: /planos",
            "Disallow: /contratos",
            "Disallow: /faturas",
            "Disallow: /api/",
            f"Sitemap: {_eleva_cam_url('/sitemap.xml')}",
            "",
        ]
    )
    return Response(corpo, mimetype="text/plain; charset=utf-8")


@cameras_bp.route("/sitemap.xml")
def sitemap_xml():
    agora = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    urls = [
        (_eleva_cam_url("/eleva-cam"), "daily", "1.0"),
    ]
    try:
        for cam in CameraService.listar(apenas_ativas=True):
            urls.append(
                (
                    _eleva_cam_url(f"/eleva-cam/{cam['slug']}"),
                    "hourly" if cam["stream_status"] == "online" else "daily",
                    "0.9",
                )
            )
    except Exception as erro:
        print(f"[eleva-cam] sitemap: {erro}")

    linhas = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ]
    for loc, freq, prioridade in urls:
        linhas.extend(
            [
                "  <url>",
                f"    <loc>{loc}</loc>",
                f"    <lastmod>{agora}</lastmod>",
                f"    <changefreq>{freq}</changefreq>",
                f"    <priority>{prioridade}</priority>",
                "  </url>",
            ]
        )
    linhas.append("</urlset>")
    return Response("\n".join(linhas) + "\n", mimetype="application/xml; charset=utf-8")


@cameras_bp.route("/eleva-cam", strict_slashes=False)
@cameras_bp.route("/cameras/ao-vivo")
def eleva_cam_home():
    try:
        cameras = CameraService.listar(apenas_ativas=True)
    except Exception as erro:
        print(f"[eleva-cam] erro ao listar cameras: {erro}")
        cameras = []

    destaque = cameras[0] if cameras else None
    clima = None
    if request.args.get("sem_clima") != "1":
        clima = _clima_da_camera(destaque)

    seo = _eleva_cam_seo(
        "/eleva-cam",
        title="Eleva Cam — Serra do Rio do Rastro Ao Vivo",
        description=(
            "Câmeras ao vivo em pontos turísticos. "
            "Serra do Rio do Rastro — Lauro Müller/SC."
        ),
    )

    try:
        return render_template(
            "eleva_cam/home.html",
            cameras=cameras,
            destaque=destaque,
            clima=clima,
            **seo,
        )
    except Exception as erro:
        import traceback
        traceback.print_exc()
        try:
            return render_template(
                "eleva_cam/home.html",
                cameras=cameras,
                destaque=destaque,
                clima=None,
                **seo,
            )
        except Exception as erro2:
            traceback.print_exc()
            return (
                "<h1>Erro eleva-cam</h1>"
                f"<pre>{erro}</pre><pre>{erro2}</pre>"
            ), 500


@cameras_bp.route("/eleva-cam/<slug>")
def eleva_cam_camera(slug):
    camera = CameraService.buscar_por_slug(slug)

    if not camera:
        return render_template(
            "eleva_cam/home.html",
            cameras=CameraService.listar(apenas_ativas=True),
            destaque=None,
            clima=None,
            erro="Câmera não encontrada ou indisponível.",
            **_eleva_cam_seo("/eleva-cam"),
        ), 404

    outras = [
        item for item in CameraService.listar(apenas_ativas=True)
        if item["id"] != camera["id"]
    ]

    clima = None
    if request.args.get("sem_clima") != "1":
        clima = _clima_da_camera(camera)

    descricao = camera["descricao"] or f"{camera['nome']} ao vivo — Eleva Cam"
    seo = _eleva_cam_seo(
        f"/eleva-cam/{camera['slug']}",
        title=f"{camera['nome']} Ao Vivo | Eleva Cam",
        description=descricao,
    )

    try:
        return render_template(
            "eleva_cam/camera.html",
            camera=camera,
            outras=outras,
            clima=clima,
            **seo,
        )
    except Exception as erro:
        print(f"[eleva-cam] erro no template camera: {erro}")
        return render_template(
            "eleva_cam/camera.html",
            camera=camera,
            outras=outras,
            clima=None,
            **seo,
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
