from datetime import datetime

from repositories.base_repository import BaseRepository

ANONIMIZADO = "*** ANONIMIZADO ***"


class LgpdTitularRepository:

    @staticmethod
    def listar_encomendas_por_contato(telefone=None, email=None):
        filtros = []
        params = []

        tel = (telefone or "").strip()
        em = (email or "").strip()

        if tel:
            filtros.append("(e.telefone = ? AND e.telefone != '' AND e.telefone IS NOT NULL)")
            params.append(tel)
        if em:
            filtros.append("(e.email = ? AND e.email != '' AND e.email IS NOT NULL)")
            params.append(em)

        if not filtros:
            return []

        where = " OR ".join(filtros)

        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT
                    e.*,
                    c.numero AS compartimento_numero,
                    a.nome AS armario_nome
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                LEFT JOIN armarios a ON a.id = c.armario
                WHERE {where}
                ORDER BY e.id DESC
            """, tuple(params)).fetchall()

    @staticmethod
    def listar_consentimentos(titular_tipo, titular_id, telefone=None, email=None):
        filtros = ["(titular_tipo = ? AND titular_id = ?)"]
        params = [titular_tipo, titular_id]

        tel = (telefone or "").strip()
        em = (email or "").strip()
        if tel:
            filtros.append("(telefone = ? AND telefone != '' AND telefone IS NOT NULL)")
            params.append(tel)
        if em:
            filtros.append("(email = ? AND email != '' AND email IS NOT NULL)")
            params.append(em)

        where = " OR ".join(filtros)

        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT *
                FROM lgpd_consentimentos
                WHERE {where}
                ORDER BY id DESC
            """, tuple(params)).fetchall()

    @staticmethod
    def listar_notificacoes_por_encomendas(encomenda_ids):
        if not encomenda_ids:
            return []
        placeholders = ",".join("?" * len(encomenda_ids))
        with BaseRepository.get_connection() as conn:
            return conn.execute(f"""
                SELECT *
                FROM notificacoes
                WHERE encomenda_id IN ({placeholders})
                ORDER BY id DESC
            """, tuple(encomenda_ids)).fetchall()

    @staticmethod
    def anonimizar_usuario(usuario_id):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        email_anon = f"anonimizado_{usuario_id}@anon.elevalocker.local"

        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE usuarios
                SET nome = ?,
                    email = ?,
                    telefone = ?,
                    marketing_opt_out = 1,
                    lgpd_anonimizado_em = ?
                WHERE id = ?
            """, (ANONIMIZADO, email_anon, ANONIMIZADO, agora, usuario_id))
            conn.commit()

    @staticmethod
    def anonimizar_encomenda(encomenda_id):
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE encomendas
                SET cliente = ?,
                    telefone = ?,
                    email = ?,
                    lgpd_anonimizado_em = ?
                WHERE id = ?
            """, (ANONIMIZADO, ANONIMIZADO, ANONIMIZADO, agora, encomenda_id))
            conn.commit()

    @staticmethod
    def anonimizar_encomendas_por_contato(telefone=None, email=None):
        encomendas = LgpdTitularRepository.listar_encomendas_por_contato(telefone, email)
        ids = []
        for enc in encomendas:
            enc = dict(enc)
            if enc.get("lgpd_anonimizado_em"):
                continue
            LgpdTitularRepository.anonimizar_encomenda(enc["id"])
            ids.append(enc["id"])
        return ids
