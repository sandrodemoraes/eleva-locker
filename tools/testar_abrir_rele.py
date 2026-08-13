#!/usr/bin/env python3
"""
Testa acionamento de relé via ESP32 (mesmo caminho da retirada no totem).

Uso:
  python tools/testar_abrir_rele.py --token 94436b42f81558231e1f0c328105be8d --rele 8
  python tools/testar_abrir_rele.py --compartimento 8
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from esp32 import Esp32Client
from services.esp32_service import Esp32Service


def main():
    parser = argparse.ArgumentParser(description="Testar abertura de relé ELEVA LOCKER")
    parser.add_argument("--esp", default="192.168.16.162", help="IP da ESP32")
    parser.add_argument("--token", help="Token ESP32 (firmware / painel)")
    parser.add_argument("--rele", type=int, help="Número do relé (1-8)")
    parser.add_argument("--compartimento", type=int, help="ID do compartimento no banco")
    parser.add_argument("--duracao", type=int, default=3, help="Segundos de acionamento")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.compartimento:
        resultado = Esp32Service.abrir_compartimento(args.compartimento, operador="testar_abrir_rele")
        label = f"compartimento_id={args.compartimento} (via banco/servidor)"
    elif args.rele and args.token:
        resultado = Esp32Client.abrir_rele(
            ip=args.esp,
            rele=args.rele,
            token=args.token,
            duracao=args.duracao,
        )
        label = f"relé {args.rele} @ {args.esp}"
    else:
        parser.error("Informe --rele + --token ou --compartimento")

    if args.json:
        print(json.dumps(resultado, indent=2, ensure_ascii=False))
    else:
        print(f"\n=== Abrir relé — {label} ===\n")
        if resultado.get("sucesso"):
            print("OK — relé acionado. Ouça o clique na placa / veja Serial Monitor.")
        else:
            print("ERRO:", resultado.get("mensagem", "falha"))
        print()

    sys.exit(0 if resultado.get("sucesso") else 1)


if __name__ == "__main__":
    main()
