import json
from datetime import datetime

import config
from repositories.base_repository import BaseRepository
from repositories.esp32_repository import Esp32Repository
from repositories.compartimento_repository import CompartimentoRepository
from services.log_service import LogService


class Esp32SyncService:
    """Sincronização servidor → ESP32 (cadastros) e ESP32 → servidor (eventos offline)."""

    @staticmethod
    def incrementar_versao(esp32_id):

        if not esp32_id:
            return

        with BaseRepository.get_connection() as conn:
            conn.execute("""
                UPDATE esp32
                SET sync_versao = COALESCE(sync_versao, 0) + 1
                WHERE id = ?
            """, (esp32_id,))
            conn.commit()

    @staticmethod
    def incrementar_por_compartimento(compartimento_id):

        comp = CompartimentoRepository.buscar_por_id(compartimento_id)

        if comp and comp.get("esp32_id"):
            Esp32SyncService.incrementar_versao(comp["esp32_id"])

    @staticmethod
    def incrementar_por_armario(armario_id):

        with BaseRepository.get_connection() as conn:
            rows = conn.execute("""
                SELECT DISTINCT esp32_id FROM compartimentos
                WHERE armario = ? AND esp32_id IS NOT NULL
            """, (armario_id,)).fetchall()

        for row in rows:
            Esp32SyncService.incrementar_versao(row["esp32_id"])

    @staticmethod
    def obter_pacote_sync(esp32_id):

        esp = Esp32Repository.buscar_por_id(esp32_id)

        if not esp:
            raise ValueError("ESP32 não encontrado.")

        esp = dict(esp)
        max_portas = config.normalizar_max_portas(esp.get("max_portas") or 16)

        with BaseRepository.get_connection() as conn:

            compartimentos = conn.execute("""
                SELECT
                    c.id,
                    c.numero,
                    c.rele,
                    c.gpio,
                    c.tamanho,
                    c.status,
                    c.armario
                FROM compartimentos c
                WHERE c.esp32_id = ?
                ORDER BY c.numero
                LIMIT ?
            """, (esp32_id, max_portas)).fetchall()

            codigos = conn.execute("""
                SELECT
                    e.id AS encomenda_id,
                    e.codigo,
                    e.cliente,
                    c.id AS compartimento_id,
                    c.numero AS compartimento_numero,
                    c.rele,
                    c.gpio
                FROM encomendas e
                JOIN compartimentos c ON c.id = e.compartimento
                WHERE c.esp32_id = ?
                  AND e.status = 'aguardando_retirada'
            """, (esp32_id,)).fetchall()

        servidor = config.APP_URL_BASE.rstrip("/")

        return {
            "versao": esp.get("sync_versao") or 1,
            "esp32_id": esp32_id,
            "nome": esp["nome"],
            "armario_id": esp.get("armario"),
            "max_portas": max_portas,
            "servidor_url": servidor,
            "rele_duracao": config.ESP32_RELE_DURACAO,
            "compartimentos": [dict(c) for c in compartimentos],
            "codigos_ativos": [dict(c) for c in codigos],
            "gerado_em": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        }

    @staticmethod
    def _evento_ja_processado(evento_uid):

        with BaseRepository.get_connection() as conn:
            row = conn.execute("""
                SELECT id FROM esp32_eventos_sync WHERE evento_uid = ?
            """, (evento_uid,)).fetchone()

        return row is not None

    @staticmethod
    def _registrar_evento(esp32_id, evento_uid, tipo, payload):

        with BaseRepository.get_connection() as conn:
            conn.execute("""
                INSERT INTO esp32_eventos_sync (esp32_id, evento_uid, tipo, payload)
                VALUES (?, ?, ?, ?)
            """, (esp32_id, evento_uid, tipo, json.dumps(payload)))
            conn.commit()

    @staticmethod
    def processar_eventos(esp32_id, eventos, esp_nome="ESP32"):

        resultados = []

        for ev in eventos:

            uid = (ev.get("uid") or "").strip()
            tipo = (ev.get("tipo") or "").strip().lower()

            if not uid or not tipo:
                resultados.append({
                    "uid": uid,
                    "sucesso": False,
                    "mensagem": "uid e tipo são obrigatórios.",
                })
                continue

            if Esp32SyncService._evento_ja_processado(uid):
                resultados.append({
                    "uid": uid,
                    "sucesso": True,
                    "mensagem": "Evento já processado (idempotente).",
                })
                continue

            try:

                if tipo == "retirada":

                    from services.encomenda_service import EncomendaService

                    codigo = (ev.get("codigo") or "").strip()

                    if not codigo:
                        raise ValueError("Código não informado.")

                    EncomendaService.retirar(
                        codigo,
                        operador=f"ESP32-OFFLINE:{esp_nome}",
                    )

                elif tipo == "abertura":

                    compartimento_id = ev.get("compartimento_id")

                    LogService.registrar(
                        compartimento_id,
                        f"ESP32:{esp_nome}",
                        ev.get("detalhe") or "Abertura registrada offline",
                    )

                elif tipo == "heartbeat_offline":

                    pass

                else:
                    raise ValueError(f"Tipo de evento desconhecido: {tipo}")

                Esp32SyncService._registrar_evento(esp32_id, uid, tipo, ev)

                resultados.append({
                    "uid": uid,
                    "sucesso": True,
                    "mensagem": "Processado.",
                })

            except ValueError as erro:

                msg = str(erro)
                if tipo == "retirada" and "inválido" in msg.lower():
                    Esp32SyncService._registrar_evento(
                        esp32_id, uid, tipo, ev,
                    )
                    resultados.append({
                        "uid": uid,
                        "sucesso": True,
                        "mensagem": "Já processado anteriormente.",
                    })
                    continue

                Esp32SyncService._registrar_evento(
                    esp32_id, uid, f"{tipo}_erro", {**ev, "erro": str(erro)},
                )

                resultados.append({
                    "uid": uid,
                    "sucesso": False,
                    "mensagem": str(erro),
                })

        Esp32SyncService.incrementar_versao(esp32_id)

        return resultados
