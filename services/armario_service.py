import sqlite3

DB = "database/elevalocker.db"


class ArmarioService:

    @staticmethod
    def listar():

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        armarios = conn.execute("""
            SELECT *
            FROM armarios
            ORDER BY nome
        """).fetchall()

        conn.close()

        return armarios

    @staticmethod
    def buscar_por_id(armario_id):

        conn = sqlite3.connect(DB)
        conn.row_factory = sqlite3.Row

        armario = conn.execute("""
            SELECT *
            FROM armarios
            WHERE id = ?
        """, (armario_id,)).fetchone()

        conn.close()

        return armario

    @staticmethod
    def inserir(dados):

        nome = (dados.get("nome") or "").strip()

        if not nome:
            raise ValueError("O nome do armário é obrigatório.")

        status = (dados.get("status") or "Ativo").strip()
        if status not in ("Ativo", "Inativo"):
            status = "Ativo"

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO armarios (
                nome,
                endereco,
                cidade,
                estado,
                status
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            nome,
            (dados.get("endereco") or "").strip(),
            (dados.get("cidade") or "").strip(),
            (dados.get("estado") or "").strip().upper()[:2],
            status,
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def atualizar(armario_id, dados):

        nome = (dados.get("nome") or "").strip()

        if not nome:
            raise ValueError("O nome do armário é obrigatório.")

        status = (dados.get("status") or "Ativo").strip()
        if status not in ("Ativo", "Inativo"):
            status = "Ativo"

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE armarios
            SET
                nome = ?,
                endereco = ?,
                cidade = ?,
                estado = ?,
                status = ?
            WHERE id = ?
        """, (
            nome,
            (dados.get("endereco") or "").strip(),
            (dados.get("cidade") or "").strip(),
            (dados.get("estado") or "").strip().upper()[:2],
            status,
            armario_id,
        ))

        conn.commit()
        conn.close()

    @staticmethod
    def excluir(armario_id):

        conn = sqlite3.connect(DB)
        cursor = conn.cursor()

        cursor.execute("""
            DELETE FROM armarios
            WHERE id = ?
        """, (armario_id,))

        conn.commit()
        conn.close()
