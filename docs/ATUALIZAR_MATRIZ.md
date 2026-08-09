# Atualizar ELEVA Locker Matriz — guia simples

> **Um comando no PC:** `tools\atualizar_matriz.bat`  
> (ou `tools\atualizar.bat` — mesmo fluxo)

---

## Resumo — o que usar

| Situação | Comando |
|----------|---------|
| Atualizar tudo (git + banco + reinício) | `tools\atualizar_matriz.bat` |
| **Backup manual (antes de mexer)** | `tools\backup_obrigatorio.bat` |
| Só conferir se está OK | `tools\verificar_matriz.bat` |
| Parar servidor | `tools\parar_servidor.bat` |
| Diagnóstico rápido | `python tools\diagnostico_bancada.py` |
| Só copiar firmware Arduino | `python tools\atualizar_matriz.py --so-firmware` |

---

## O que deu errado antes (e como evitar)

| Problema | Causa | Solução |
|----------|--------|---------|
| `/sensor/8` → 404 | Firmware **sem** `SENSOR_GPIO` | Abrir `firmware/elevalocker_sync/elevalocker_sync.ino` |
| Totem não abre porta | Totem id **3**, ESP na **Bancada id 4** | Só **ELEVA Locker Matriz** + `TOTEM_ARMARIO_ID=3` |
| Armários vazios | Script gravou **SQLite**, servidor lia **Postgres** | `.env` **sem** `DATABASE_URL` na bancada |
| Token 403 | Token `.env` ≠ firmware ≠ banco | `atualizar_matriz.bat` alinha automaticamente |
| Relé não clica | Placa BESTER = **LOW ligado** | `RELE_ATIVO_LOW = true` no firmware |
| `python qual_servidor.bat` | `.bat` não usa `python` | Só: `tools\qual_servidor.bat` |
| Vários ESP no painel | Bancada Teste + Matriz | Script remove duplicados automaticamente |

---

## Atualização normal (1 clique)

```cmd
cd C:\ElevaLocker
tools\atualizar_matriz.bat
```

Isso faz automaticamente:

1. Para o servidor na porta 15000  
2. **Backup OBRIGATÓRIO** — banco + `.env` (aborta se falhar)  
3. Backup no **D:** se o disco existir  
4. `git pull` da branch estável  
5. Copia firmware para pasta Arduino  
6. `setup_oficial` — armário Matriz + 8 compartimentos  
7. Remove ESP/armário **Bancada Teste** duplicados  
8. Reinicia `app.py`  
9. Alinha token ESP no banco  
10. Verificação final (`verificar_matriz`)

> **Margem de erro zero:** se o backup falhar, **nada** é alterado depois disso.

---

## Depois do script — Arduino (só se mudou firmware)

1. Abrir: `firmware\elevalocker_sync\elevalocker_sync.ino`
2. Conferir `ESP32_TOKEN` = token do painel (ESP Matriz 8ch)
3. **Fechar Serial Monitor** → Upload
4. Serial: `Sync OK v… — 8 compartimentos`

---

## `.env` mínimo (bancada / Matriz)

```env
TOTEM_ARMARIO_ID=3
ESP32_TOKEN=2e5bb4db71d8330be8bae43b13ac19f6
ESP32_MODO_SIMULACAO=0
TOTEM_DEPOSITO_PIN=2026
```

**Não** use `DATABASE_URL=` na bancada (usa SQLite em `database/elevalocker.db`).

---

## URLs fixas

| O quê | URL |
|-------|-----|
| Armário | http://192.168.16.130:15000/armarios/3 |
| Totem | http://192.168.16.130:15000/totem/3 |
| Teste relés | http://192.168.16.130:15000/esp32/bancada |
| ESP local | http://192.168.16.162/?token=TOKEN |

---

## Parar / diagnosticar / backup

```cmd
tools\backup_obrigatorio.bat
tools\parar_servidor.bat
tools\qual_servidor.bat
tools\verificar_matriz.bat
tools\backup_disco_d.bat
python tools\diagnostico_bancada.py --token SEU_TOKEN
```

Restaurar backup: painel → **Configurações → Restaurar backup #1**
