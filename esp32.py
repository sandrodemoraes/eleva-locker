import urllib.request
import urllib.error
import json

import config


class Esp32Client:
    """
    Cliente HTTP para comunicação com dispositivos ESP32.
    Protocolo: GET http://{ip}:{porta}/abrir/{rele}?token={token}&duracao={seg}
    """

    @staticmethod
    def abrir_rele(ip, rele, token=None, porta=80, duracao=None):

        if not ip:
            return {"sucesso": False, "mensagem": "ESP32 sem IP configurado."}

        if not rele:
            return {"sucesso": False, "mensagem": "Compartimento sem relé configurado."}

        if config.ESP32_MODO_SIMULACAO:
            return {
                "sucesso": True,
                "mensagem": f"[SIMULAÇÃO] Relé {rele} acionado por {duracao or config.ESP32_RELE_DURACAO}s",
                "simulado": True,
            }

        duracao = duracao or config.ESP32_RELE_DURACAO
        token = token or config.ESP32_TOKEN

        url = f"http://{ip}:{porta}/abrir/{rele}?token={token}&duracao={duracao}"

        try:

            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=config.ESP32_HTTP_TIMEOUT) as resp:

                corpo = resp.read().decode("utf-8")

                try:
                    dados = json.loads(corpo)
                except json.JSONDecodeError:
                    dados = {"raw": corpo}

                return {
                    "sucesso": True,
                    "mensagem": "Relé acionado com sucesso.",
                    "dados": dados,
                }

        except urllib.error.URLError as erro:

            return {
                "sucesso": False,
                "mensagem": f"ESP32 inacessível: {erro.reason}",
            }

        except Exception as erro:

            return {
                "sucesso": False,
                "mensagem": f"Erro ao acionar relé: {erro}",
            }

    @staticmethod
    def status(ip, porta=80, token=None):

        if not ip:
            return {"sucesso": False, "mensagem": "ESP32 sem IP."}

        if config.ESP32_MODO_SIMULACAO:
            return {"sucesso": True, "online": True, "simulado": True}

        token = token or config.ESP32_TOKEN
        url = f"http://{ip}:{porta}/status?token={token}"

        try:

            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=config.ESP32_HTTP_TIMEOUT) as resp:

                return {
                    "sucesso": True,
                    "dados": json.loads(resp.read().decode("utf-8")),
                }

        except Exception as erro:

            return {"sucesso": False, "mensagem": str(erro)}

    @staticmethod
    def ler_sensor(ip, rele, token=None, porta=80):

        if not ip:
            return {"sucesso": False, "mensagem": "ESP32 sem IP configurado."}

        if not rele:
            return {"sucesso": False, "mensagem": "Relé não informado."}

        if config.ESP32_MODO_SIMULACAO:
            return {
                "sucesso": True,
                "simulado": True,
                "sensor": True,
                "fechada": True,
                "aberta": False,
                "rele": rele,
            }

        token = token or config.ESP32_TOKEN
        url = f"http://{ip}:{porta}/sensor/{rele}?token={token}"

        try:

            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=config.ESP32_HTTP_TIMEOUT) as resp:

                dados = json.loads(resp.read().decode("utf-8"))

                return {
                    "sucesso": True,
                    "sensor": bool(dados.get("sensor", True)),
                    "fechada": bool(dados.get("fechada", False)),
                    "aberta": bool(dados.get("aberta", not dados.get("fechada", False))),
                    "rele": dados.get("rele", rele),
                    "gpio": dados.get("gpio"),
                    "dados": dados,
                }

        except urllib.error.URLError as erro:

            return {
                "sucesso": False,
                "mensagem": f"ESP32 inacessível: {erro.reason}",
            }

        except Exception as erro:

            return {
                "sucesso": False,
                "mensagem": f"Erro ao ler sensor: {erro}",
            }

    @staticmethod
    def ler_sensores(ip, token=None, porta=80):

        if not ip:
            return {"sucesso": False, "mensagem": "ESP32 sem IP configurado."}

        if config.ESP32_MODO_SIMULACAO:
            portas = [
                {"rele": r, "fechada": True, "aberta": False}
                for r in range(1, 9)
            ]
            return {"sucesso": True, "simulado": True, "sensor": True, "portas": portas}

        token = token or config.ESP32_TOKEN
        url = f"http://{ip}:{porta}/sensores?token={token}"

        try:

            req = urllib.request.Request(url, method="GET")

            with urllib.request.urlopen(req, timeout=config.ESP32_HTTP_TIMEOUT) as resp:

                dados = json.loads(resp.read().decode("utf-8"))

                return {
                    "sucesso": True,
                    "sensor": bool(dados.get("sensor", True)),
                    "portas": dados.get("portas", []),
                    "dados": dados,
                }

        except Exception as erro:

            return {"sucesso": False, "mensagem": str(erro)}
