"""Busca destinatários (moradores) para autocomplete no totem."""

from repositories.base_repository import BaseRepository


class TotemDestinatarioService:

    @staticmethod
    def buscar(termo, armario_id=None, limit=12):
        termo = (termo or "").strip()
        if len(termo) < 2:
            return []

        like = f"%{termo}%"
        vistos = {}
        resultados = []

        def adicionar(nome, telefone, origem):
            chave = nome.strip().lower()
            if not chave or chave in vistos:
                return
            tel = (telefone or "").strip()
            vistos[chave] = True
            resultados.append({
                "nome": nome.strip(),
                "telefone": tel,
                "origem": origem,
            })

        with BaseRepository.get_connection() as conn:
            params = [like]
            filtro_arm = ""
            if armario_id is not None:
                filtro_arm = "AND c.armario = ?"
                params.append(armario_id)

            rows = conn.execute(f"""
                SELECT e.cliente, e.telefone, e.data_entrada
                FROM encomendas e
                LEFT JOIN compartimentos c ON c.id = e.compartimento
                WHERE e.cliente LIKE ? COLLATE NOCASE
                  AND TRIM(e.cliente) != ''
                  {filtro_arm}
                ORDER BY e.data_entrada DESC
            """, tuple(params)).fetchall()

            for row in rows:
                adicionar(row["cliente"], row["telefone"], "encomenda")
                if len(resultados) >= limit:
                    return resultados[:limit]

            params_u = [like]
            filtro_u = "AND (u.armario_id IS NULL OR u.armario_id = ?)" if armario_id else ""
            if armario_id is not None:
                params_u.append(armario_id)

            usuarios = conn.execute(f"""
                SELECT u.nome, u.telefone
                FROM usuarios u
                WHERE u.status = 1
                  AND u.perfil = 'Usuário'
                  AND u.nome LIKE ? COLLATE NOCASE
                  {filtro_u}
                ORDER BY u.nome
            """, tuple(params_u)).fetchall()

            for row in usuarios:
                adicionar(row["nome"], row["telefone"], "cadastro")
                if len(resultados) >= limit:
                    break

        return resultados[:limit]
