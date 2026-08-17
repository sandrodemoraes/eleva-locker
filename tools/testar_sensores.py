#!/usr/bin/env python3
"""
Testa sensores das 8 portas via ESP32 (ou simulador).

Uso:
  python tools/testar_sensores.py
  python tools/testar_sensores.py --esp 192.168.16.162 --token SEU_TOKEN
  python tools/testar_sensores.py --compartimento 5
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from esp32 import Esp32Client
from services.esp32_service import Esp32Service
from services.compartimento_service import CompartimentoService


def main():
    parser = argparse.ArgumentParser(description="Testar sensores de porta ELEVA LOCKER")
    parser.add_argument("--esp", help="IP da ESP32")
    parser.add_argument("--token", help="Token ESP32")
    parser.add_argument("--porta-http", type=int, default=80)
    parser.add_argument("--rele", type=int, help="Testar só um relé (1-8)")
    parser.add_argument("--compartimento", type=int, help="Ler sensor via compartimento_id no banco")
    parser.add_argument("--json", action="store_true", help="Saída JSON")
    args = parser.parse_args()

    if args.compartimento:
        resultado = Esp32Service.ler_sensor_compartimento(args.compartimento)
        comp = CompartimentoService.buscar_por_id(args.compartimento)
        label = f"Compartimento #{comp['numero']} (relé {comp['rele']})"
    elif args.esp:
        if args.rele:
            resultado = Esp32Client.ler_sensor(args.esp, args.rele, args.token, args.porta_http)
            label = f"Relé {args.rele} @ {args.esp}"
        else:
            resultado = Esp32Client.ler_sensores(args.esp, args.token, args.porta_http)
            label = f"Todas portas @ {args.esp}"
    else:
        import config
        ip = config.APP_URL_BASE.replace("http://", "").split(":")[0] if hasattr(config, "APP_URL_BASE") else None
        parser.error("Informe --esp IP ou --compartimento ID")

    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
        return

    print(f"\n=== Sensor — {label} ===\n")

    if not resultado.get("sucesso"):
        print("ERRO:", resultado.get("mensagem", "falha"))
        sys.exit(1)

    if "portas" in resultado:
        for p in resultado["portas"]:
            estado = "FECHADA" if p.get("fechada") else "ABERTA"
            print(f"  Relé {p['rele']}: {estado}")
    else:
        estado = "FECHADA" if resultado.get("fechada") else "ABERTA"
        print(f"  Estado: {estado}")
        if resultado.get("gpio"):
            print(f"  GPIO: {resultado['gpio']}")

    print("\nOK — sensor respondendo.\n")


if __name__ == "__main__":
    main()
