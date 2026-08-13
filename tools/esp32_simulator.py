"""
Simulador ESP32 para testes locais.
Uso: python tools/esp32_simulator.py [porta]
Endpoints:
  GET  /abrir/{rele}?token=...&duracao=3
  GET  /status?token=...
  GET  /sensor/{rele}?token=...
  GET  /sensores?token=...
  GET  /sensor/{rele}/fechar?token=...  (simula porta fechada)
"""
import json
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

TOKEN = "eleva-esp32-token-2026"
RELES_ATIVOS = {}
# True = porta fechada (sensor NC em curto)
PORTA_FECHADA = {i: True for i in range(1, 9)}


class Esp32Handler(BaseHTTPRequestHandler):

    def log_message(self, format, *args):
        print(f"[ESP32-SIM] {args[0]}")

    def _json(self, code, data):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())

    def do_GET(self):

        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)
        token = params.get("token", [""])[0]

        if token != TOKEN:
            self._json(403, {"erro": "Token inválido"})
            return

        if parsed.path.startswith("/abrir/"):

            rele = int(parsed.path.split("/")[-1])
            duracao = int(params.get("duracao", ["3"])[0])
            RELES_ATIVOS[rele] = duracao
            if rele in PORTA_FECHADA:
                PORTA_FECHADA[rele] = False

            self._json(200, {
                "sucesso": True,
                "rele": rele,
                "duracao": duracao,
                "mensagem": f"Relé {rele} acionado por {duracao}s — porta ABERTA (sim)",
            })
            return

        if parsed.path.startswith("/sensor/") and parsed.path.endswith("/fechar"):
            rele = int(parsed.path.split("/")[2])
            PORTA_FECHADA[rele] = True
            self._json(200, {
                "sucesso": True,
                "rele": rele,
                "fechada": True,
                "aberta": False,
                "mensagem": f"Porta {rele} FECHADA (sim)",
            })
            return

        if parsed.path.startswith("/sensor/"):

            rele = int(parsed.path.split("/")[-1])
            fechada = PORTA_FECHADA.get(rele, True)
            self._json(200, {
                "rele": rele,
                "sensor": True,
                "fechada": fechada,
                "aberta": not fechada,
            })
            return

        if parsed.path == "/sensores":

            portas = [
                {
                    "rele": r,
                    "fechada": PORTA_FECHADA.get(r, True),
                    "aberta": not PORTA_FECHADA.get(r, True),
                }
                for r in range(1, 9)
            ]
            self._json(200, {"sensor": True, "portas": portas})
            return

        if parsed.path == "/status":

            self._json(200, {
                "online": True,
                "reles_ativos": RELES_ATIVOS,
                "firmware": "elevalocker-sim-1.1-sensor",
            })
            return

        self._json(404, {"erro": "Rota não encontrada"})


if __name__ == "__main__":

    porta = int(sys.argv[1]) if len(sys.argv) > 1 else 8080

    print(f"Simulador ESP32 rodando em http://0.0.0.0:{porta}")
    print(f"Token: {TOKEN}")
    print("Sensores sim: /sensor/1 .. /sensor/8 | fechar: /sensor/1/fechar")

    HTTPServer(("0.0.0.0", porta), Esp32Handler).serve_forever()
