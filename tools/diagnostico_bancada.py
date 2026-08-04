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
            WHERE a.nome = 'Bancada Teste'
            ORDER BY c.numero
        """).fetchall()

        print(f"\nCompartimentos Bancada Teste: {len(comps)}")
        for c in comps:
            print(f"  #{c['numero']} | {c['tamanho'] or 'M'} | relé {c['rele']} | esp32_id={c['esp32_id']}")

    print("\n" + "=" * 60)
    print("URLs:")
    print("  Painel armário: http://192.168.16.130:15000/armarios")
    print("  Totem ESP:   http://192.168.16.162/")
    print("  Teste relé:  http://192.168.16.162/abrir/1?token=TOKEN&duracao=3")
    print("=" * 60)


if __name__ == "__main__":
    main()
