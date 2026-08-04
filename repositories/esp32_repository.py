from datetime import datetime, timedelta

import config
from repositories.base_repository import BaseRepository


class Esp32Repository:

    @staticmethod
    def listar():

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    a.nome AS armario_nome,
                    (
                        SELECT COUNT(*)
                        FROM compartimentos c
                        WHERE c.esp32_id = e.id
                    ) AS total_compartimentos
                FROM esp32 e
                LEFT JOIN armarios a ON a.id = e.armario
                ORDER BY e.nome
            """).fetchall()

    @staticmethod
    def buscar_por_id(esp32_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    a.nome AS armario_nome
                FROM esp32 e
                LEFT JOIN armarios a ON a.id = e.armario
                WHERE e.id = ?
            """, (esp32_id,)).fetchone()

    @staticmethod
    def buscar_por_token(token):

        if not token:
            return None

        token = token.strip()

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM esp32
                WHERE TRIM(token) = ?
            """, (token,)).fetchone()

    @staticmethod
    def buscar_por_mac(mac):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT *
                FROM esp32
                WHERE mac = ?
            """, (mac,)).fetchone()

    @staticmethod
    def criar(dados):

        with BaseRepository.get_connection() as conn:

            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO esp32 (
                    nome, ip, mac, armario, status, token, porta, ultimo_heartbeat,
                    max_portas, sync_versao
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                dados["nome"],
                dados.get("ip"),
                dados.get("mac"),
                dados.get("armario"),
                dados.get("status", "offline"),
                dados["token"],
                dados.get("porta", 80),
                dados.get("ultimo_heartbeat"),
                dados.get("max_portas", 16),
                dados.get("sync_versao", 1),
            ))

            conn.commit()

            return cursor.lastrowid

    @staticmethod
    def atualizar(esp32_id, dados):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE esp32
                SET
                    nome = ?,
                    ip = ?,
                    mac = ?,
                    armario = ?,
                    status = ?,
                    token = ?,
                    porta = ?,
                    max_portas = ?
                WHERE id = ?
            """, (
                dados["nome"],
                dados.get("ip"),
                dados.get("mac"),
                dados.get("armario"),
                dados.get("status", "offline"),
                dados.get("token"),
                dados.get("porta", 80),
                dados.get("max_portas", 16),
                esp32_id,
            ))

            conn.commit()

    @staticmethod
    def atualizar_heartbeat(esp32_id, ip=None):

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        with BaseRepository.get_connection() as conn:

            if ip:

                conn.execute("""
                    UPDATE esp32
                    SET ultimo_heartbeat = ?, status = 'online', ip = ?
                    WHERE id = ?
                """, (agora, ip, esp32_id))

            else:

                conn.execute("""
                    UPDATE esp32
                    SET ultimo_heartbeat = ?, status = 'online'
                    WHERE id = ?
                """, (agora, esp32_id))

            conn.commit()

    @staticmethod
    def marcar_offline(esp32_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE esp32
                SET status = 'offline'
                WHERE id = ?
            """, (esp32_id,))

            conn.commit()

    @staticmethod
    def marcar_offline_expirados():

        limite = datetime.now() - timedelta(seconds=config.ESP32_HEARTBEAT_TIMEOUT)
        limite_str = limite.strftime("%Y-%m-%d %H:%M:%S")

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE esp32
                SET status = 'offline'
                WHERE status = 'online'
                  AND (
                    ultimo_heartbeat IS NULL
                    OR ultimo_heartbeat < ?
                  )
            """, (limite_str,))

            conn.commit()

    @staticmethod
    def listar_por_armario(armario_id):

        with BaseRepository.get_connection() as conn:

            return conn.execute("""
                SELECT
                    e.*,
                    (
                        SELECT COUNT(*)
                        FROM compartimentos c
                        WHERE c.esp32_id = e.id
                    ) AS total_compartimentos
                FROM esp32 e
                WHERE e.armario = ?
                ORDER BY e.nome
            """, (armario_id,)).fetchall()

    @staticmethod
    def excluir(esp32_id):

        with BaseRepository.get_connection() as conn:

            conn.execute("""
                UPDATE compartimentos
                SET esp32_id = NULL
                WHERE esp32_id = ?
            """, (esp32_id,))

            conn.execute("""
                DELETE FROM esp32
                WHERE id = ?
            """, (esp32_id,))

            conn.commit()

    @staticmethod
    def contar_online(site_id=None):

        with BaseRepository.get_connection() as conn:

            if site_id is not None:
                return conn.execute("""
                    SELECT COUNT(*) AS total
                    FROM esp32 e
                    JOIN armarios a ON a.id = e.armario
                    WHERE e.status = 'online' AND a.site_id = ?
                """, (site_id,)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total
                FROM esp32
                WHERE status = 'online'
            """).fetchone()["total"]

    @staticmethod
    def contar(site_id=None):

        with BaseRepository.get_connection() as conn:

            if site_id is not None:
                return conn.execute("""
                    SELECT COUNT(*) AS total
                    FROM esp32 e
                    JOIN armarios a ON a.id = e.armario
                    WHERE a.site_id = ?
                """, (site_id,)).fetchone()["total"]

            return conn.execute("""
                SELECT COUNT(*) AS total FROM esp32
            """).fetchone()["total"]
