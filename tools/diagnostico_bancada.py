#!/usr/bin/env python3
"""
Diagnóstico rápido — bancada ESP32 + banco.
Uso: py tools/diagnostico_bancada.py
     py tools/diagnostico_bancada.py --token 51ec130a...
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository


def main():
    parser = argparse.ArgumentParser(description="Diagnóstico bancada ELEVA LOCKER")
    parser.add_argument("--token", help="Token do firmware para comparar")
    args = parser.parse_args()

    print("=" * 60)
    print("DIAGNÓSTICO BANCADA")
    print("=" * 60)

    with BaseRepository.get_connection() as conn:
        esps = conn.execute("""
            SELECT id, nome, ip, token, status, ultimo_heartbeat, sync_versao, max_portas
            FROM esp32 ORDER BY id
        """).fetchall()

        print(f"\nESP32 cadastrados: {len(esps)}")
        if not esps:
            print("  ⚠ NENHUM ESP — rode: py tools/setup_bancada.py --ip-esp 192.168.16.162")
        for e in esps:
            print(f"\n  id={e['id']} | {e['nome']}")
            print(f"  IP: {e['ip'] or '—'} | Status: {e['status']}")
            print(f"  Token: {e['token']}")
            print(f"  Sync v{e['sync_versao']} | Heartbeat: {e['ultimo_heartbeat'] or 'nunca'}")
            if args.token:
                ok = args.token.strip() == (e["token"] or "").strip()
                print(f"  Token firmware {'✅ IGUAL' if ok else '❌ DIFERENTE'}")

        comps = conn.execute("""
            SELECT c.numero, c.tamanho, c.rele, c.gpio, c.esp32_id, a.nome AS armario
            FROM compartimentos c
            JOIN armarios a ON a.id = c.armario
            WHERE a.nome IN ('ELEVA Locker Matriz', 'Bancada Teste')
            ORDER BY a.nome, c.numero
        """).fetchall()

        matriz = [c for c in comps if c["armario"] == "ELEVA Locker Matriz"]
        bancada = [c for c in comps if c["armario"] == "Bancada Teste"]

        print(f"\nCompartimentos ELEVA Locker Matriz: {len(matriz)}")
        for c in matriz[:8]:
            print(f"  #{c['numero']} | {c['tamanho'] or 'M'} | relé {c['rele']} | esp32_id={c['esp32_id']}")

        if bancada:
            print(f"\nCompartimentos Bancada Teste (remover): {len(bancada)}")
            for c in bancada:
                print(f"  #{c['numero']} | {c['tamanho'] or 'M'} | relé {c['rele']} | esp32_id={c['esp32_id']}")
            print("  → Rode: py tools/limpar_bancada_teste.py")

    print("\n" + "=" * 60)
    print("URLs:")
    print("  Painel Matriz: http://192.168.16.130:15000/armarios/3")
    print("  Totem:         http://192.168.16.130:15000/totem/3")
    print("  Teste relés:   http://192.168.16.130:15000/esp32/bancada")
    print("  ESP local:     http://192.168.16.162/?token=TOKEN")
    print("\nAtualizar: tools\\atualizar_matriz.bat")
    print("Verificar: tools\\verificar_matriz.bat")
    print("=" * 60)


if __name__ == "__main__":
    main()
