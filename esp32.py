import urllib.request
import urllib.error
import json

import config


def _mensagem_erro_esp32(erro):
    """Mensagem amigável para totem/painel (sem jargão Python)."""
    texto = str(erro).lower()
    reason = ""
    if isinstance(erro, urllib.error.URLError) and erro.reason is not None:
        reason = str(erro.reason).lower()
    if "timed out" in texto or "timeout" in reason or "timeout" in texto:
        return "Placa não respondeu. Verifique se a ESP32 está ligada e no Wi-Fi."
    if "refused" in reason or "recus" in reason:
        return "Conexão recusada. Placa desligada ou IP incorreto."
    if "no route" in reason or "unreachable" in reason:
        return "Placa inacessível na rede local."
    if isinstance(erro, urllib.error.URLError):
        return "ESP32 inacessível na rede."
    return "Falha ao comunicar com a ESP32."


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

        except urllib.error.HTTPError as erro:

            corpo = ""
            try:
                corpo = erro.read().decode("utf-8", errors="replace")
            except Exception:
                pass

            if erro.code == 403:
                return {
                    "sucesso": False,
                    "mensagem": "Token ESP32 rejeitado — alinhe token do banco com o firmware.",
                    "http": erro.code,
                    "dados": corpo,
                }

            return {
                "sucesso": False,
                "mensagem": f"ESP32 respondeu HTTP {erro.code}: {corpo or erro.reason}",
                "http": erro.code,
            }

        except urllib.error.URLError as erro:

            return {
                "sucesso": False,
                "mensagem": _mensagem_erro_esp32(erro),
            }

        except Exception as erro:

            return {
                "sucesso": False,
                "mensagem": _mensagem_erro_esp32(erro),
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

        except urllib.error.URLError as erro:

            return {
                "sucesso": False,
                "mensagem": _mensagem_erro_esp32(erro),
            }

        except Exception as erro:

            return {
                "sucesso": False,
                "mensagem": _mensagem_erro_esp32(erro),
            }

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
                "mensagem": _mensagem_erro_esp32(erro),
            }

        except Exception as erro:

            return {
                "sucesso": False,
                "mensagem": _mensagem_erro_esp32(erro),
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

            return {"sucesso": False, "mensagem": _mensagem_erro_esp32(erro)}
