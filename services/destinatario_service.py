"""Busca destinatários (moradores) para autocomplete no depósito."""

from db.connection import coluna_existe, get_engine
from repositories.base_repository import BaseRepository


class DestinatarioService:

    @staticmethod
    def _filtro_armario_usuario(armario_id, tem_armario_id):
        if armario_id is None or not tem_armario_id:
            return "", ()
        return """
            AND (
                u.armario_id IS NULL
                OR u.armario_id = ?
                OR u.armario_id NOT IN (SELECT id FROM armarios)
            )
        """, (armario_id,)

    @staticmethod
    def buscar(termo, armario_id=None, limit=12):
        termo = (termo or "").strip()
        if len(termo) < 2:
            return []

        like = f"%{termo}%"
        vistos = {}
        resultados = []

        def adicionar(nome, telefone, email=None, origem="encomenda", usuario_id=None):
            chave = nome.strip().lower()
            if not chave or chave in vistos:
                return
            vistos[chave] = True
            item = {
                "id": usuario_id,
                "nome": nome.strip(),
                "telefone": (telefone or "").strip(),
                "email": (email or "").strip(),
                "origem": origem,
            }
            resultados.append(item)

        with BaseRepository.get_connection() as conn:
            cursor = conn.cursor()
            tem_armario_id = coluna_existe(cursor, "usuarios", "armario_id", get_engine())

            params = [like]
            filtro_arm = ""
            if armario_id is not None:
                filtro_arm = "AND c.armario = ?"
                params.append(armario_id)

            rows = conn.execute(f"""
                SELECT e.cliente, e.telefone, e.email, e.data_entrada
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                WHERE e.cliente LIKE ? COLLATE NOCASE
                  AND TRIM(e.cliente) != ''
                  {filtro_arm}
                ORDER BY e.data_entrada DESC
            """, tuple(params)).fetchall()

            for row in rows:
                adicionar(
                    row["cliente"],
                    row["telefone"],
                    row["email"],
                    "encomenda",
                )
                if len(resultados) >= limit:
                    return resultados[:limit]

            filtro_sql, filtro_params = DestinatarioService._filtro_armario_usuario(
                armario_id, tem_armario_id
            )
            params_u = [like, *filtro_params, limit]

            usuarios = conn.execute(f"""
                SELECT u.id, u.nome, u.telefone, u.email
                FROM usuarios u
                WHERE u.status = 1
                  AND u.perfil = 'Usuário'
                  AND u.nome LIKE ? COLLATE NOCASE
                  {filtro_sql}
                ORDER BY u.nome
                LIMIT ?
            """, tuple(params_u)).fetchall()

            for row in usuarios:
                adicionar(
                    row["nome"],
                    row["telefone"],
                    row["email"],
                    "cadastro",
                    row["id"],
                )
                if len(resultados) >= limit:
                    break

        return resultados[:limit]
