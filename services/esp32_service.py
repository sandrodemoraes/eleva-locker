import config
from esp32 import Esp32Client
from repositories.esp32_repository import Esp32Repository
from repositories.compartimento_repository import CompartimentoRepository
from services.log_service import LogService


class Esp32Service:

    @staticmethod
    def listar():
        Esp32Repository.marcar_offline_expirados()
        return Esp32Repository.listar()

    @staticmethod
    def buscar_por_id(esp32_id):

        esp = Esp32Repository.buscar_por_id(esp32_id)

        if not esp:
            raise ValueError("ESP32 não encontrado.")

        return esp

    @staticmethod
    def buscar_por_token(token):

        if not token:
            return None

        return Esp32Repository.buscar_por_token(token)

    @staticmethod
    def criar(dados):

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do ESP32 é obrigatório.")

        dados["nome"] = nome
        dados["token"] = dados.get("token") or config.gerar_token_esp32()

        max_portas = config.normalizar_max_portas(dados.get("max_portas") or 16)
        dados["max_portas"] = max_portas

        esp_id = Esp32Repository.criar(dados)

        from services.esp32_portas_service import Esp32PortasService
        if dados.get("armario"):
            try:
                Esp32PortasService.sincronizar_compartimentos(esp_id, max_portas)
            except ValueError:
                pass

        return esp_id

    @staticmethod
    def atualizar(esp32_id, dados):

        esp_antigo = Esp32Service.buscar_por_id(esp32_id)

        nome = dados.get("nome", "").strip()

        if not nome:
            raise ValueError("Nome do ESP32 é obrigatório.")

        dados["nome"] = nome

        if "max_portas" in dados:
            dados["max_portas"] = config.normalizar_max_portas(dados.get("max_portas") or 16)

        Esp32Repository.atualizar(esp32_id, dados)

        from services.esp32_sync_service import Esp32SyncService
        from services.esp32_portas_service import Esp32PortasService

        max_novo = dados.get("max_portas", esp_antigo.get("max_portas"))
        if max_novo and esp_antigo.get("armario"):
            try:
                Esp32PortasService.sincronizar_compartimentos(esp32_id, max_novo)
            except ValueError:
                Esp32SyncService.incrementar_versao(esp32_id)
        else:
            Esp32SyncService.incrementar_versao(esp32_id)

    @staticmethod
    def excluir(esp32_id):

        Esp32Service.buscar_por_id(esp32_id)
        Esp32Repository.excluir(esp32_id)

    @staticmethod
    def heartbeat(token, ip=None, mac=None):

        esp = Esp32Repository.buscar_por_token(token)

        if not esp:
            raise ValueError("Token inválido.")

        if mac and not esp["mac"]:
            esp32_id = esp["id"]
            Esp32Repository.atualizar(esp32_id, {
                "nome": esp["nome"],
                "ip": ip or esp["ip"],
                "mac": mac,
                "armario": esp["armario"],
                "status": "online",
                "token": esp["token"],
                "porta": esp["porta"] if "porta" in esp.keys() else 80,
            })

        Esp32Repository.atualizar_heartbeat(esp["id"], ip)

        return esp["id"]

    @staticmethod
    def registrar_evento(token, compartimento_id, acao, usuario="ESP32"):

        esp = Esp32Repository.buscar_por_token(token)

        if not esp:
            raise ValueError("Token inválido.")

        LogService.registrar(
            compartimento_id,
            usuario,
            f"[ESP32 {esp['nome']}] {acao}",
        )

    @staticmethod
    def abrir_compartimento(compartimento_id, operador="Sistema"):

        compartimento = CompartimentoRepository.buscar_por_id(compartimento_id)

        if not compartimento:
            raise ValueError("Compartimento não encontrado.")

        rele = compartimento["rele"]

        if not rele:
            return {
                "sucesso": False,
                "mensagem": "Compartimento sem relé configurado. Abertura manual necessária.",
                "manual": True,
            }

        esp32_id = compartimento["esp32_id"]

        if not esp32_id:

            return {
                "sucesso": False,
                "mensagem": "Compartimento sem ESP32 vinculado. Abertura manual necessária.",
                "manual": True,
            }

        esp = Esp32Repository.buscar_por_id(esp32_id)

        if not esp:
            return {
                "sucesso": False,
                "mensagem": "ESP32 não encontrado.",
                "manual": True,
            }

        porta = esp["porta"] if "porta" in esp.keys() and esp["porta"] else 80

        resultado = Esp32Client.abrir_rele(
            ip=esp["ip"],
            rele=rele,
            token=esp["token"],
            porta=porta,
        )

        if resultado["sucesso"]:

            LogService.registrar(
                compartimento_id,
                operador,
                f"Relé {rele} acionado via ESP32 {esp['nome']}",
            )

        return resultado

    @staticmethod
    def listar_codigos_ativos(armario_id=None):

        from repositories.encomenda_repository import EncomendaRepository

        with __import__("repositories.base_repository", fromlist=["BaseRepository"]).BaseRepository.get_connection() as conn:

            if armario_id:

                rows = conn.execute("""
                    SELECT e.codigo, c.numero AS compartimento, c.rele
                    FROM encomendas e
                    JOIN compartimentos c ON c.id = e.compartimento
                    WHERE e.status = 'aguardando_retirada'
                      AND c.armario = ?
                """, (armario_id,)).fetchall()

            else:

                rows = conn.execute("""
                    SELECT e.codigo, c.numero AS compartimento, c.rele
                    FROM encomendas e
                    JOIN compartimentos c ON c.id = e.compartimento
                    WHERE e.status = 'aguardando_retirada'
                """).fetchall()

        return [dict(r) for r in rows]

    @staticmethod
    def testar_conexao(esp32_id):

        esp = Esp32Service.buscar_por_id(esp32_id)
        porta = esp["porta"] if "porta" in esp.keys() and esp["porta"] else 80

        return Esp32Client.status(esp["ip"], porta, esp["token"])
