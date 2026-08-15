#!/usr/bin/env python3
"""
Atualiza tamanhos dos compartimentos da bancada (1–4 P, 5–6 M, 7 G, 8 GG).

Uso:
  py tools/fix_tamanhos_bancada.py
  py tools/fix_tamanhos_bancada.py --nome-esp "ESP Bancada 8ch"
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")

from database import criar_banco

criar_banco()

from repositories.base_repository import BaseRepository
from services.esp32_sync_service import Esp32SyncService

TAMANHO_POR_NUMERO = {
    1: "P",
    2: "P",
    3: "P",
    4: "P",
    5: "M",
    6: "M",
    7: "G",
    8: "GG",
}


def main():
    parser = argparse.ArgumentParser(description="Corrige tamanhos da bancada 8ch")
    parser.add_argument("--nome-esp", default="ESP Bancada 8ch", help="Nome do ESP no cadastro")
    parser.add_argument("--armario", default="Bancada Teste", help="Nome do armário (fallback)")
    args = parser.parse_args()

    with BaseRepository.get_connection() as conn:
        esp = conn.execute(
            "SELECT id, nome, armario FROM esp32 WHERE nome = ? LIMIT 1",
            (args.nome_esp,),
        ).fetchone()

        if not esp:
            print(f"ESP '{args.nome_esp}' não encontrado. Cadastre ou rode setup_bancada.py")
            sys.exit(1)

        esp_id = esp["id"]
        armario_id = esp["armario"]

        if not armario_id:
            arm = conn.execute(
                "SELECT id FROM armarios WHERE nome = ? LIMIT 1",
                (args.armario,),
            ).fetchone()
            if arm:
                armario_id = arm["id"]

        rows = conn.execute("""
            SELECT id, numero, tamanho, armario
            FROM compartimentos
            WHERE esp32_id = ?
            ORDER BY numero
        """, (esp_id,)).fetchall()

        if not rows and armario_id:
            rows = conn.execute("""
                SELECT id, numero, tamanho, armario
                FROM compartimentos
                WHERE armario = ?
                ORDER BY numero
            """, (armario_id,)).fetchall()

    if not rows:
        print("Nenhum compartimento encontrado para este ESP/armário.")
        print("Rode: py tools/setup_bancada.py --ip-esp SEU_IP_ESP")
        sys.exit(1)

    print(f"ESP: {args.nome_esp} (id={esp_id})")
    print(f"Compartimentos encontrados: {len(rows)}\n")
    print(f"{'#':>3}  {'Antes':>6}  {'Depois':>6}  {'Status':>10}")
    print("-" * 32)

    alterados = 0
    with BaseRepository.get_connection() as conn:
        for row in rows:
            num = int(row["numero"])
            novo = TAMANHO_POR_NUMERO.get(num)
            if not novo:
                print(f"{num:>3}  {row['tamanho'] or '—':>6}  {'—':>6}  {'ignorado':>10}")
                continue

            antes = row["tamanho"] or "M"
            if antes == novo:
                status = "ok"
            else:
                conn.execute(
                    "UPDATE compartimentos SET tamanho = ? WHERE id = ?",
                    (novo, row["id"]),
                )
                status = "atualizado"
                alterados += 1

            print(f"{num:>3}  {antes:>6}  {novo:>6}  {status:>10}")

        conn.commit()

    if alterados:
        Esp32SyncService.incrementar_versao(esp_id)
        print(f"\n{alterados} compartimento(s) atualizado(s). Sync ESP incrementado.")
    else:
        print("\nNada a alterar — tamanhos já estavam corretos.")

    print("\nConfira em: http://localhost:15000/compartimentos")
    print("(filtro: Bancada Teste)")


if __name__ == "__main__":
    main()
