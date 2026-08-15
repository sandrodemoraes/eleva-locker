#!/usr/bin/env python3
"""
Backup dos arquivos .ino de cada ESP32 no disco D: (ou pasta local).

Copia o sketch que contém o TOKEN de cada placa cadastrada no banco
e grava ficha.txt com IP, armário, RELE_ATIVO_LOW, etc.

Uso:
  py tools/backup_firmware_esp.py
  py tools/backup_firmware_esp.py --dest D:\\ElevaLockerBackup\\firmware
  py tools/backup_firmware_esp.py --local   # só backups/firmware_esp/

Integrado em tools/backup_disco_d.py e tools/backup_obrigatorio.py
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("SKIP_BACKUP", "1")

DISCO_D_FIRMWARE = Path(r"D:\ElevaLockerBackup\firmware")
LOCAL_FIRMWARE = ROOT / "backups" / "firmware_esp"

# Pastas preferidas (nome da pasta -> slug no backup)
PASTAS_PRIORIDADE = (
    "elevalocker_matriz",
    "elevalocker_bancada2",
    "elevalocker_sync",
)


def slugificar(texto: str) -> str:
    s = (texto or "esp").lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return s.strip("-") or "esp"


def listar_inos_firmware() -> list[Path]:
    base = ROOT / "firmware"
    if not base.is_dir():
        return []
    inos = sorted(base.rglob("*.ino"))
    # Prioridade: pastas nomeadas primeiro, depois demais
    def chave(p: Path) -> tuple:
        pasta = p.parent.name
        try:
            prio = PASTAS_PRIORIDADE.index(pasta)
        except ValueError:
            prio = len(PASTAS_PRIORIDADE)
        return (prio, pasta, p.name)

    return sorted(inos, key=chave)


def parse_ino(conteudo: str) -> dict:
    def extrair(pattern: str) -> str | None:
        m = re.search(pattern, conteudo, re.MULTILINE)
        return m.group(1).strip() if m else None

    token = extrair(r'ESP32_TOKEN\s*=\s*"([^"]+)"')
    servidor = extrair(r'SERVIDOR_URL\s*=\s*"([^"]+)"')
    wifi = extrair(r'WIFI_SSID\s*=\s*"([^"]+)"')
    rele = extrair(r"RELE_ATIVO_LOW\s*=\s*(true|false)")
    return {
        "token": token,
        "servidor_url": servidor,
        "wifi_ssid": wifi,
        "rele_ativo_low": rele,
    }


def achar_ino_por_token(inos: list[Path], token: str | None) -> Path | None:
    if not token:
        return None
    token = token.strip()
    for ino in inos:
        try:
            texto = ino.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if token in texto:
            parsed = parse_ino(texto)
            if parsed.get("token") == token:
                return ino
    return None


def montar_ficha(esp: dict, ino: Path | None, parsed: dict) -> str:
    linhas = [
        "ELEVA LOCKER — backup firmware ESP",
        f"Gerado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "",
        f"ESP id      : {esp.get('id')}",
        f"Nome        : {esp.get('nome')}",
        f"IP          : {esp.get('ip') or '(nao definido)'}",
        f"Armario id  : {esp.get('armario')}",
        f"Armario     : {esp.get('armario_nome') or ''}",
        f"Max portas  : {esp.get('max_portas')}",
        f"Token (DB)  : {esp.get('token')}",
        "",
    ]
    if ino:
        linhas.extend([
            f"Arquivo .ino: {ino.relative_to(ROOT)}",
            f"Token (.ino): {parsed.get('token') or '?'}",
            f"Servidor    : {parsed.get('servidor_url') or '?'}",
            f"Wi-Fi       : {parsed.get('wifi_ssid') or '?'}",
            f"RELE_ATIVO_LOW: {parsed.get('rele_ativo_low') or '?'}",
        ])
    else:
        linhas.append("Arquivo .ino: NENHUM encontrado com este token no projeto.")
        linhas.append("Grave o sketch e rode este backup de novo.")

    linhas.extend([
        "",
        "Restaurar no Arduino IDE:",
        "  1. Abra a pasta do .ino copiado (pasta e arquivo com mesmo nome)",
        "  2. Confira placa: ESP32C3 (Matriz) ou ESP32 Dev Module (Bancada 2)",
        "  3. Upload na COM correta",
    ])
    return "\n".join(linhas) + "\n"


def backup_esp(esp: dict, inos: list[Path], destino_base: Path) -> dict:
    token = esp.get("token")
    ino = achar_ino_por_token(inos, token)

    slug = slugificar(esp.get("nome") or f"esp-{esp.get('id')}")
    pasta = destino_base / f"esp{esp['id']}_{slug}"
    pasta.mkdir(parents=True, exist_ok=True)

    parsed = {}
    if ino:
        texto = ino.read_text(encoding="utf-8", errors="replace")
        parsed = parse_ino(texto)
        # Copia mantendo nome do sketch (Arduino exige pasta = nome do .ino)
        nome_ino = ino.name
        shutil.copy2(ino, pasta / nome_ino)
        # Cópia legível com data no nome (histórico)
        stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        shutil.copy2(ino, pasta / f"{ino.stem}_{stamp}.ino")

    ficha = montar_ficha(esp, ino, parsed)
    (pasta / "ficha.txt").write_text(ficha, encoding="utf-8")

    return {
        "esp_id": esp["id"],
        "nome": esp.get("nome"),
        "ip": esp.get("ip"),
        "armario": esp.get("armario_nome"),
        "ino": str(ino.relative_to(ROOT)) if ino else None,
        "destino": str(pasta),
        "ok": ino is not None,
    }


def carregar_esps():
    from database import criar_banco

    criar_banco()
    from repositories.esp32_repository import Esp32Repository

    return [dict(row) for row in Esp32Repository.listar()]


def executar_backup(destino_base: Path) -> tuple[bool, list[dict]]:
    destino_base.mkdir(parents=True, exist_ok=True)
    inos = listar_inos_firmware()
    esps = carregar_esps()

    if not esps:
        print("  AVISO: nenhuma ESP cadastrada no banco.")
        return True, []

    resultados = []
    for esp in esps:
        info = backup_esp(esp, inos, destino_base)
        resultados.append(info)
        status = "OK" if info["ok"] else "SEM .INO"
        origem = info["ino"] or "(token nao encontrado em firmware/)"
        print(f"  [{status}] ESP {info['esp_id']} {info['nome']}")
        print(f"         {origem}")
        print(f"         -> {info['destino']}")

    manifest = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "destino": str(destino_base),
        "esps": resultados,
    }
    (destino_base / "manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    (destino_base / "_ultimo_backup.txt").write_text(stamp, encoding="utf-8")

    sem_ino = [r for r in resultados if not r["ok"]]
    if sem_ino:
        print()
        print(f"  AVISO: {len(sem_ino)} ESP(s) sem .ino correspondente ao token.")
        print("  Salve cada sketch em firmware/ com o TOKEN correto e rode de novo.")

    return True, resultados


def main():
    parser = argparse.ArgumentParser(description="Backup .ino de cada ESP no disco D:")
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help=r"Pasta destino (padrao: D:\ElevaLockerBackup\firmware)",
    )
    parser.add_argument(
        "--local",
        action="store_true",
        help="Grava so em backups/firmware_esp/ (sem exigir D:)",
    )
    args = parser.parse_args()

    print("=" * 58)
    print("  ELEVA LOCKER — Backup firmware ESP (.ino)")
    print("=" * 58)
    print()

    if args.local:
        destino = LOCAL_FIRMWARE
    elif args.dest:
        destino = args.dest
    else:
        if not Path("D:/").exists():
            print("Disco D: nao encontrado.")
            print("Use --local ou conecte D: e rode de novo.")
            print(f"Alternativa: py tools\\backup_firmware_esp.py --dest C:\\ElevaLocker\\backups\\firmware_esp")
            return 1
        destino = DISCO_D_FIRMWARE

    print(f"Destino: {destino}")
    print()

    ok, _ = executar_backup(destino)
    if not ok:
        return 1

    print()
    print("Backup firmware concluido!")
    print(f"  Pasta: {destino}")
    print("  Cada ESP: .ino + ficha.txt + copia com data")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
