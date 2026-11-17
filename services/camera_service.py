import re
import sqlite3
from datetime import datetime

DB = "database/elevalocker.db"

STREAM_STATUS = ("online", "offline", "manutencao")


def _slugify(texto):
    mapa = str.maketrans(
        "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
        "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
    )
    base = (texto or "").translate(mapa).lower().strip()
    base = re.sub(r"[^a-z0-9\s-]", "", base)
    base = re.sub(r"[\s_-]+", "-", base).strip("-")
    return base or "camera"


class CameraService:

    @staticmethod
    def listar(apenas_ativas=False):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        if apenas_ativas:
            cameras = conn.execute("""
                SELECT *
                FROM cameras
                WHERE status = 1
                ORDER BY ordem ASC, nome ASC
            """).fetchall()
        else:
            cameras = conn.execute("""
                SELECT *
                FROM cameras
                ORDER BY ordem ASC, nome ASC
            """).fetchall()

        conn.close()
        return cameras

    @staticmethod
    def buscar_por_id(camera_id):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        camera = conn.execute("""
            SELECT *
            FROM cameras
            WHERE id = ?
        """, (camera_id,)).fetchone()

        conn.close()
        return camera

    @staticmethod
    def buscar_por_slug(slug):
        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        camera = conn.execute("""
            SELECT *
            FROM cameras
            WHERE slug = ? AND status = 1
        """, (slug,)).fetchone()

        conn.close()
        return camera

    @staticmethod
    def slug_existe(slug, ignorar_id=None):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        if ignorar_id:
            cursor.execute("""
                SELECT id FROM cameras
                WHERE slug = ? AND id != ?
            """, (slug, ignorar_id))
        else:
            cursor.execute("""
                SELECT id FROM cameras
                WHERE slug = ?
            """, (slug,))

        existe = cursor.fetchone() is not None
        conn.close()
        return existe

    @staticmethod
    def normalizar(dados, camera_id=None):
        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("Informe o nome da câmera.")

        slug = (dados.get("slug") or "").strip() or _slugify(nome)
        slug = _slugify(slug)

        if CameraService.slug_existe(slug, ignorar_id=camera_id):
            raise ValueError("Já existe uma câmera com este slug.")

        stream_status = (dados.get("stream_status") or "offline").strip().lower()
        if stream_status not in STREAM_STATUS:
            stream_status = "offline"

        try:
            status = int(dados.get("status", 1))
        except (TypeError, ValueError):
            status = 1

        try:
            ordem = int(dados.get("ordem", 0) or 0)
        except (TypeError, ValueError):
            ordem = 0

        latitude = dados.get("latitude")
        longitude = dados.get("longitude")

        try:
            latitude = float(latitude) if latitude not in (None, "") else None
        except (TypeError, ValueError):
            latitude = None

        try:
            longitude = float(longitude) if longitude not in (None, "") else None
        except (TypeError, ValueError):
            longitude = None

        return {
            "nome": nome,
            "slug": slug,
            "local": (dados.get("local") or "").strip(),
            "cidade": (dados.get("cidade") or "").strip(),
            "estado": (dados.get("estado") or "").strip().upper()[:2],
            "descricao": (dados.get("descricao") or "").strip(),
            "youtube_video_id": (dados.get("youtube_video_id") or "").strip(),
            "youtube_channel_url": (dados.get("youtube_channel_url") or "").strip(),
            "stream_status": stream_status,
            "latitude": latitude,
            "longitude": longitude,
            "ordem": ordem,
            "status": 1 if status == 1 else 0,
        }

    @staticmethod
    def inserir(dados):
        dados = CameraService.normalizar(dados)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO cameras (
                nome,
                slug,
                local,
                cidade,
                estado,
                descricao,
                youtube_video_id,
                youtube_channel_url,
                stream_status,
                latitude,
                longitude,
                ordem,
                status
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados["nome"],
            dados["slug"],
            dados["local"],
            dados["cidade"],
            dados["estado"],
            dados["descricao"],
            dados["youtube_video_id"],
            dados["youtube_channel_url"],
            dados["stream_status"],
            dados["latitude"],
            dados["longitude"],
            dados["ordem"],
            dados["status"],
        ))

        conn.commit()
        camera_id = cursor.lastrowid
        conn.close()
        return camera_id

    @staticmethod
    def atualizar(camera_id, dados):
        dados = CameraService.normalizar(dados, camera_id=camera_id)
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE cameras
            SET
                nome = ?,
                slug = ?,
                local = ?,
                cidade = ?,
                estado = ?,
                descricao = ?,
                youtube_video_id = ?,
                youtube_channel_url = ?,
                stream_status = ?,
                latitude = ?,
                longitude = ?,
                ordem = ?,
                status = ?,
                atualizado_em = ?
            WHERE id = ?
        """, (
            dados["nome"],
            dados["slug"],
            dados["local"],
            dados["cidade"],
            dados["estado"],
            dados["descricao"],
            dados["youtube_video_id"],
            dados["youtube_channel_url"],
            dados["stream_status"],
            dados["latitude"],
            dados["longitude"],
            dados["ordem"],
            dados["status"],
            agora,
            camera_id,
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def excluir(camera_id):
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM cameras WHERE id = ?", (camera_id,))
        conn.commit()
        conn.close()
