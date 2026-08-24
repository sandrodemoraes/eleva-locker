#!/usr/bin/env python3
"""
Diagnostica e corrige mapeamento relé/compartimento Bancada 24 portas.

Problema comum: portas 9-24 com rele=9..24 (errado) em vez de rele local 1-8.

Uso:
  py tools/diagnostico_reles_bancada.py
  py tools/diagnostico_reles_bancada.py --corrigir
"""
import argparse
import os
import sys
import urllib.error
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.armario_repository import ArmarioRepository
from repositories.compartimento_repository import CompartimentoRepository
from repositories.esp32_repository import Esp32Repository
from services.esp32_portas_service import Esp32PortasService

ARMARIO_PADRAO = 3
MODULOS = (
    (1, 8),
    (9, 16),
    (17, 24),
)


def rele_esperado(numero, porta_inicial):
    return numero - porta_inicial + 1


def testar_esp_ip(ip, token, rele=1):
    url = f"http://{ip}/abrir/{rele}?token={token}&duracao=1"
    try:
        with urllib.request.urlopen(url, timeout=4) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body[:120]
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", errors="replace")[:120]
    except Exception as e:
        return 0, str(e)[:120]


def diagnosticar(armario_id):
    arm = ArmarioRepository.buscar_por_id(armario_id)
    if not arm:
        raise SystemExit(f"Armário id={armario_id} não encontrado.")

    comps = CompartimentoRepository.listar(armario_id)
    esps = Esp32Repository.listar_por_armario(armario_id)
    esps_por_id = {e["id"]: e for e in esps}

    print("=" * 72)
    print(f"  DIAGNÓSTICO RELÉS — {arm['nome']} (id={armario_id})")
    print("=" * 72)

    erros = []
    print("\n  Compartimentos:")
    print("  #  | relé | ESP (IP)           | esperado | status")
    print("  " + "-" * 65)

    for c in sorted(comps, key=lambda x: x["numero"]):
        num = c["numero"]
        esp = esps_por_id.get(c["esp32_id"])
        esp_nome = (esp["nome"] if esp else "?")[:12]
        ip = esp["ip"] if esp else "—"

        porta_ini = None
        for pi, pf in MODULOS:
            if pi <= num <= pf:
                porta_ini = pi
                break

        exp_rele = rele_esperado(num, porta_ini) if porta_ini else "?"
        exp_esp_idx = MODULOS.index((porta_ini, porta_ini + 7)) + 1 if porta_ini else "?"

        ok_rele = c["rele"] == exp_rele if isinstance(exp_rele, int) else False

        esps_ord = sorted(esps, key=lambda e: Esp32PortasService.resolver_porta_inicial(e["id"]))
        esp_esperado = esps_ord[exp_esp_idx - 1] if isinstance(exp_esp_idx, int) and len(esps_ord) >= exp_esp_idx else None
        ok_esp = esp and esp_esperado and esp["id"] == esp_esperado["id"]

        flags = []
        if not ok_rele:
            flags.append(f"relé deveria ser {exp_rele}")
        if esp and porta_ini and len(esps) >= exp_esp_idx and not ok_esp:
            flags.append(f"ESP deveria ser módulo {exp_esp_idx}")

        st = "OK" if not flags else "ERRO: " + ", ".join(flags)
        if flags:
            erros.append(num)

        print(
            f"  {num:2} | {c['rele']:4} | {esp_nome} ({ip})"
            f" | relé {exp_rele} mod{exp_esp_idx} | {st}"
        )

    print("\n  Teste HTTP relé 1 em cada ESP:")
    for esp in sorted(esps, key=lambda e: Esp32PortasService.resolver_porta_inicial(e["id"])):
        if not esp["ip"]:
            print(f"    {esp['nome']}: sem IP")
            continue
        code, msg = testar_esp_ip(esp["ip"], esp["token"], rele=1)
        if code == 200 and "sucesso" in msg.lower():
            st = "OK — token + relé 1"
        elif code == 403:
            st = "TOKEN INVÁLIDO — regrave firmware com token do painel"
        else:
            st = f"HTTP {code} — {msg}"
        print(f"    {esp['nome']} ({esp['ip']}): {st}")
        if code == 403:
            erros.append(f"token:{esp['ip']}")

    print("\n  " + "-" * 65)
    if erros:
        print(f"  {len(erros)} problema(s) encontrado(s).")
        print("  Correção: py tools\\diagnostico_reles_bancada.py --corrigir")
    else:
        print("  Mapeamento OK. Se relé não clica, verifique RELE_ATIVO_LOW no firmware.")
    print("=" * 72)
    return len(erros) == 0


def corrigir(armario_id):
    import config

    arm = ArmarioRepository.buscar_por_id(armario_id)
    if not arm:
        raise SystemExit(f"Armário id={armario_id} não encontrado.")

    total = config.normalizar_max_portas(arm["max_portas"] or 24)
    ArmarioRepository.atualizar(armario_id, {
        "nome": arm["nome"],
        "endereco": arm["endereco"],
        "cidade": arm["cidade"],
        "estado": arm["estado"],
        "status": arm["status"],
        "empresa_id": arm["empresa_id"],
        "site_id": arm["site_id"],
        "max_portas": total,
    })

    esps = Esp32Repository.listar_por_armario(armario_id)
    esps = sorted(esps, key=lambda e: Esp32PortasService.resolver_porta_inicial(e["id"]))

    print("\n  Ressincronizando compartimentos (relé local 1-8 por ESP)...")
    for i, esp in enumerate(esps):
        porta_inicial = 1 + (i * 8)
        Esp32Repository.atualizar(esp["id"], {
            "nome": esp["nome"],
            "ip": esp["ip"],
            "mac": esp["mac"] or "",
            "armario": armario_id,
            "status": esp["status"],
            "token": esp["token"],
            "porta": esp["porta"] or 80,
            "max_portas": 8,
            "porta_inicial": porta_inicial,
        })
        r = Esp32PortasService.sincronizar_compartimentos(
            esp["id"], 8, porta_inicial=porta_inicial,
        )
        print(
            f"    {esp['nome']}: #{r['porta_inicial']}–#{r['porta_final']} "
            f"relés 1–{r['max_portas']}"
        )

    print("\n  Aguarde sync na ESP (~1 min) ou reinicie as placas.")
    print("  Teste: py tools\\validar_portas_bancada.py --amostra\n")


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico relés Bancada 24 portas")
    parser.add_argument("--armario-id", type=int, default=ARMARIO_PADRAO)
    parser.add_argument("--corrigir", action="store_true", help="Ressincroniza relés 1-8 por ESP")
    args = parser.parse_args()

    if args.corrigir:
        corrigir(args.armario_id)
    ok = diagnosticar(args.armario_id)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
