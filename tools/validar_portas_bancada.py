#!/usr/bin/env python3
"""
Valida compartimentos do armário Bancada (24 portas, 3× ESP).

Uso:
  py tools/validar_portas_bancada.py --listar
  py tools/validar_portas_bancada.py --amostra          # abre #1, #9, #17
  py tools/validar_portas_bancada.py --abrir 5          # abre compartimento #5
  py tools/validar_portas_bancada.py --sensores         # lê sensores das 3 ESPs
  py tools/validar_portas_bancada.py --todas --confirmar  # abre 1..24 (cuidado!)
"""
import argparse
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.esp32_repository import Esp32Repository
from services.esp32_service import Esp32Service

ARMARIO_PADRAO = 3
AMOSTRA = (1, 9, 17)


def listar(armario_id):
    arm = ArmarioRepository.buscar_por_id(armario_id)
    if not arm:
        raise SystemExit(f"Armário id={armario_id} não encontrado.")

    comps = CompartimentoRepository.listar(armario_id)
    esps = {e["id"]: e for e in Esp32Repository.listar_por_armario(armario_id)}

    print("=" * 70)
    print(f"  {arm['nome']} (id={armario_id}) — {len(comps)} compartimentos")
    print(f"  max_portas armário: {arm['max_portas']}")
    print("=" * 70)

    for esp in esps.values():
        st = esp["status"] or "?"
        print(f"\n  ESP {esp['nome']} | {esp['ip']} | {st}")

    print("\n  #  | relé | GPIO | ESP              | status")
    print("  " + "-" * 60)
    for c in sorted(comps, key=lambda x: x["numero"]):
        esp = esps.get(c["esp32_id"])
        esp_nome = (esp["nome"] if esp else "?")[:16]
        print(
            f"  {c['numero']:2} | {c['rele']:4} | {c['gpio'] or '—':4} | "
            f"{esp_nome:16} | {c['status']}"
        )

    esperado = arm["max_portas"] or 24
    if len(comps) != esperado:
        print(f"\n  AVISO: esperado {esperado} compartimentos, encontrado {len(comps)}")
        print("  Rode: tools\\configurar_bancada_24_portas.bat")
    else:
        print(f"\n  OK — {len(comps)} compartimentos cadastrados.")
    print()


def abrir_numero(armario_id, numero, pausa=2):
    comp = CompartimentoRepository.buscar_por_armario_numero(armario_id, numero)
    if not comp:
        print(f"  #{numero}: NÃO ENCONTRADO no banco")
        return False

    esp = Esp32Repository.buscar_por_id(comp["esp32_id"]) if comp["esp32_id"] else None
    esp_info = f"{esp['nome']} @ {esp['ip']}" if esp else "sem ESP"

    r = Esp32Service.abrir_compartimento(comp["id"], operador="validar_portas")
    ok = r.get("sucesso")
    mark = "OK" if ok else "ERRO"
    print(f"  #{numero} relé {comp['rele']} ({esp_info}): {mark}", end="")
    if not ok:
        print(f" — {r.get('mensagem', '?')}")
        if esp and esp.get("ip"):
            tok = (esp.get("token") or "")[:8]
            print(
                f"       Teste direto: http://{esp['ip']}/abrir/{comp['rele']}"
                f"?token={esp['token']}&duracao=3"
            )
    else:
        print(" — ouviu clique na placa?")
        if esp and esp.get("ip"):
            print(
                f"       Se NÃO clicou: RELE_ATIVO_LOW no firmware "
                f"(false=Dev, true=C3) ou token errado na placa"
            )
    if pausa:
        time.sleep(pausa)
    return ok


def ler_sensores_esp(esp):
    r = Esp32Service.ler_sensores_esp(esp["id"])
    print(f"\n  {esp['nome']} ({esp['ip']}):")
    if not r.get("sucesso"):
        print(f"    ERRO: {r.get('mensagem', '?')}")
        return False
    for p in r.get("portas", []):
        estado = "FECHADA" if p.get("fechada") else "ABERTA"
        print(f"    relé {p['rele']}: {estado}")
    return True


def main():
    parser = argparse.ArgumentParser(description="Validar portas armário Bancada 24")
    parser.add_argument("--armario-id", type=int, default=ARMARIO_PADRAO)
    parser.add_argument("--listar", action="store_true", help="Lista mapeamento # → ESP → relé")
    parser.add_argument("--abrir", type=int, metavar="N", help="Abre compartimento número N")
    parser.add_argument("--amostra", action="store_true", help="Abre #1, #9 e #17 (1 por ESP)")
    parser.add_argument("--todas", action="store_true", help="Abre compartimentos 1..24")
    parser.add_argument("--confirmar", action="store_true", help="Obrigatório com --todas")
    parser.add_argument("--sensores", action="store_true", help="Lê sensores das 3 ESPs")
    parser.add_argument("--pausa", type=int, default=2, help="Segundos entre aberturas")
    args = parser.parse_args()

    if not any([args.listar, args.abrir, args.amostra, args.todas, args.sensores]):
        args.listar = True

    if args.listar:
        listar(args.armario_id)

    if args.sensores:
        print("=== SENSORES ===")
        esps = Esp32Repository.listar_por_armario(args.armario_id)
        for esp in esps:
            ler_sensores_esp(esp)
        print()

    if args.abrir:
        print(f"=== ABRIR #{args.abrir} ===")
        abrir_numero(args.armario_id, args.abrir, pausa=0)
        print()

    if args.amostra:
        print("=== AMOSTRA (1 ESP cada) — confira clique em #1, #9, #17 ===")
        ok = 0
        for n in AMOSTRA:
            if abrir_numero(args.armario_id, n, pausa=args.pausa):
                ok += 1
        print(f"\n  Resultado: {ok}/{len(AMOSTRA)} OK\n")

    if args.todas:
        if not args.confirmar:
            print("Use --todas --confirmar para abrir as 24 portas em sequência.")
            sys.exit(1)
        comps = CompartimentoRepository.listar(args.armario_id)
        print(f"=== ABRINDO {len(comps)} PORTAS ===")
        ok = 0
        for c in sorted(comps, key=lambda x: x["numero"]):
            if abrir_numero(args.armario_id, c["numero"], pausa=args.pausa):
                ok += 1
        print(f"\n  Resultado: {ok}/{len(comps)} OK\n")


if __name__ == "__main__":
    main()
