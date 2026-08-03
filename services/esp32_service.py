import sqlite3

DB = "database/elevalocker.db"


class Esp32Service:

    @staticmethod
    def listar():

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        dispositivos = conn.execute("""
            SELECT
                e.id,
                e.nome,
                e.ip,
                e.mac,
                e.armario,
                e.status,
                a.nome AS armario_nome
            FROM esp32 e
            LEFT JOIN armarios a ON a.id = e.armario
            ORDER BY e.nome
        """).fetchall()

        conn.close()

        return dispositivos

    @staticmethod
    def inserir(dados):

        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("O nome do ESP32 é obrigatório.")

        status = (dados.get("status") or "Ativo").strip()
        if status not in ("Ativo", "Inativo", "Offline"):
            status = "Ativo"

        armario = dados.get("armario")
        if armario in ("", None):
            armario = None
        else:
            armario = int(armario)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO esp32 (
                nome,
                ip,
                mac,
                armario,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            (dados.get("ip") or "").strip(),
            (dados.get("mac") or "").strip().upper(),
            armario,
            status,
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def atualizar(esp32_id, dados):

        nome = (dados.get("nome") or "").strip()
        if not nome:
            raise ValueError("O nome do ESP32 é obrigatório.")

        status = (dados.get("status") or "Ativo").strip()
        if status not in ("Ativo", "Inativo", "Offline"):
            status = "Ativo"

        armario = dados.get("armario")
        if armario in ("", None):
            armario = None
        else:
            armario = int(armario)

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE esp32
            SET
                nome = ?,
                ip = ?,
                mac = ?,
                armario = ?,
                status = ?
            WHERE id = ?
        """, (
            nome,
            (dados.get("ip") or "").strip(),
            (dados.get("mac") or "").strip().upper(),
            armario,
            status,
            esp32_id,
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def excluir(esp32_id):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM esp32
            WHERE id = ?
        """, (esp32_id,))

        conn.commit()
        conn.close()
