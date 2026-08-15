"""Busca destinatários (moradores) para autocomplete no totem."""

import re

import config
from repositories.base_repository import BaseRepository
from services.notificacao_service import NotificacaoService


class TotemDestinatarioService:

    @staticmethod
    def _filtro_armario(armario_id):
        if armario_id is None:
            return "", ()
        # NULL, mesmo armário, ou armário apagado (id órfão) — morador continua no autocomplete
        return """
            AND (
                u.armario_id IS NULL
                OR u.armario_id = ?
                OR u.armario_id NOT IN (SELECT id FROM armarios)
            )
        """, (armario_id,)

    @staticmethod
    def _digits(telefone):
        return re.sub(r"\D", "", telefone or "")

    @staticmethod
    def buscar(termo, armario_id=None, limit=12):
        termo = (termo or "").strip()
        if len(termo) < 1:
            return []

        if config.TOTEM_DEPOSITO_SOMENTE_CADASTRADO:
            return TotemDestinatarioService._buscar_cadastrados(termo, armario_id, limit)

        like = f"%{termo}%"
        vistos = {}
        resultados = []

        def adicionar(nome, telefone, origem, usuario_id=None):
            chave = nome.strip().lower()
            if not chave or chave in vistos:
                return
            tel = (telefone or "").strip()
            vistos[chave] = True
            item = {
                "id": usuario_id,
                "nome": nome.strip(),
                "telefone": tel,
                "origem": origem,
            }
            resultados.append(item)

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

            for item in TotemDestinatarioService._buscar_cadastrados(termo, armario_id, limit):
                adicionar(item["nome"], item["telefone"], "cadastro", item.get("id"))
                if len(resultados) >= limit:
                    break

        return resultados[:limit]

    @staticmethod
    def _buscar_cadastrados(termo, armario_id=None, limit=12):
        like = f"%{termo.strip()}%"
        filtro_sql, filtro_params = TotemDestinatarioService._filtro_armario(armario_id)

        with BaseRepository.get_connection() as conn:
            rows = conn.execute(f"""
                SELECT u.id, u.nome, u.telefone
                FROM usuarios u
                WHERE u.status = 1
                  AND u.perfil = 'Usuário'
                  AND u.nome LIKE ? COLLATE NOCASE
                  {filtro_sql}
                ORDER BY u.nome
                LIMIT ?
            """, (like, *filtro_params, limit)).fetchall()

        return [
            {
                "id": row["id"],
                "nome": row["nome"],
                "telefone": (row["telefone"] or "").strip(),
                "origem": "cadastro",
            }
            for row in rows
        ]

    @staticmethod
    def resolver_cadastrado(nome, telefone=None, armario_id=None, usuario_id=None):
        """Valida morador cadastrado; retorna dados oficiais para o depósito."""
        nome = (nome or "").strip()
        if not nome:
            raise ValueError("Informe o destinatário.")

        filtro_sql, filtro_params = TotemDestinatarioService._filtro_armario(armario_id)
        tel_digits = TotemDestinatarioService._digits(telefone)

        with BaseRepository.get_connection() as conn:
            if usuario_id is not None:
                row = conn.execute(f"""
                    SELECT u.id, u.nome, u.telefone, u.email
                    FROM usuarios u
                    WHERE u.id = ?
                      AND u.status = 1
                      AND u.perfil = 'Usuário'
                      {filtro_sql}
                """, (usuario_id, *filtro_params)).fetchone()
                if not row:
                    raise ValueError("Morador não cadastrado ou inativo.")
                if nome.lower() != row["nome"].strip().lower():
                    raise ValueError(
                        "Selecione o morador na lista — nome não confere com o cadastro."
                    )
                return TotemDestinatarioService._montar_destinatario(row, telefone)

            rows = conn.execute(f"""
                SELECT u.id, u.nome, u.telefone, u.email
                FROM usuarios u
                WHERE u.status = 1
                  AND u.perfil = 'Usuário'
                  AND LOWER(TRIM(u.nome)) = LOWER(?)
                  {filtro_sql}
            """, (nome, *filtro_params)).fetchall()

        if not rows:
            raise ValueError(
                "Morador não cadastrado. Cadastre em Usuários (perfil Morador) "
                "ou selecione da lista."
            )

        if len(rows) > 1 and tel_digits:
            filtrados = [
                r for r in rows
                if TotemDestinatarioService._digits(r["telefone"]) == tel_digits
            ]
            if len(filtrados) == 1:
                rows = filtrados
            elif not filtrados:
                raise ValueError("Telefone não confere com o morador cadastrado.")

        if len(rows) > 1:
            raise ValueError("Há mais de um morador com esse nome — selecione da lista.")

        return TotemDestinatarioService._montar_destinatario(rows[0], telefone)

    @staticmethod
    def _montar_destinatario(row, telefone_informado):
        tel_cadastro = (row["telefone"] or "").strip()
        tel_informado = (telefone_informado or "").strip()

        if config.NOTIF_WHATSAPP_ATIVO:
            tel_final = tel_cadastro or tel_informado
            if not tel_final:
                raise ValueError(
                    f"Morador {row['nome']} não tem telefone cadastrado. "
                    "Atualize o cadastro antes de depositar."
                )
            _, erro_tel = NotificacaoService.validar_telefone_br(tel_final)
            if erro_tel:
                raise ValueError(erro_tel)
        else:
            tel_final = tel_cadastro or tel_informado

        return {
            "id": row["id"],
            "nome": row["nome"],
            "telefone": tel_final,
            "email": (row["email"] or "").strip(),
        }
