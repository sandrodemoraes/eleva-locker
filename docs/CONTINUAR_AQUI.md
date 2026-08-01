# CONTINUAR AQUI — Retomada do projeto

> Última atualização: 01/08/2026  
> Estado: ESP32 offline-first implementado, aguardando teste físico na placa.

---

## Onde paramos

| Item | Status |
|------|--------|
| Fases 1–5 (operacional → escala) | ✅ PRs #1–#5 |
| Edição de usuários | ✅ PR fase-5 (commit eafc53b) |
| ESP32 sync offline 8–32 portas | ✅ PR #6 — branch `cursor/esp32-offline-sync-c05c` |
| Firmware novo | ✅ `firmware/elevalocker_sync.ino` |
| Seu firmware antigo (standalone) | ⚠️ Substituir pelo novo para integrar com Flask |
| Teste físico ESP + relé GPIO16 | ⏳ Pendente quando voltar |

---

## Comandos para executar ao voltar (Windows / VS Code)

### 1. Atualizar código (branch mais completa)

```powershell
cd C:\ElevaLocker
git fetch origin
git checkout cursor/esp32-offline-sync-c05c
git pull origin cursor/esp32-offline-sync-c05c
pip install -r requirements.txt
python app.py
```

Abrir: http://localhost:15000  
Login: `sandro.demoraes@gmail.com` + sua senha

### 2. Cadastrar ESP no painel (antes de gravar firmware)

1. **ESP32** → Novo dispositivo  
   - Nome: ex. `ESP Matriz`  
   - Armário: vincular  
   - **Max portas:** 8, 16 ou 32  
   - Copiar o **token** gerado  

2. **Compartimentos** → Para porta 1 (teste físico):  
   - Relé: `1`  
   - ESP32: selecionar o cadastrado  
   - **GPIO:** `16`  

3. Anotar **IP do PC** na rede (ex: `192.168.1.10`) — não use `localhost` na ESP.

### 3. Gravar firmware na ESP32 (Arduino IDE)

1. Instalar biblioteca **ArduinoJson 6.x**  
2. Abrir: `firmware/elevalocker_sync.ino`  
3. Editar no topo do arquivo:

```cpp
const char* WIFI_SSID     = "ELEVA - ENERGIA SOLAR";
const char* WIFI_PASSWORD = "sua_senha";
const char* SERVIDOR_URL  = "http://192.168.x.x:15000";  // IP do PC
const char* ESP32_TOKEN   = "token_copiado_do_painel";
```

4. Placa: ESP32 Dev Module → Upload  
5. Serial Monitor 115200 → confirmar IP da ESP  

### 4. Teste rápido

| Teste | Como |
|-------|------|
| Sync | Painel ESP32 → ícone Wi-Fi (testar) → deve ficar online |
| Abrir relé | Compartimentos → botão cadeado |
| Depósito | Encomendas → depositar → sync na ESP (~60s ou reiniciar ESP) |
| Retirada offline | Desligar roteador Wi-Fi → `http://IP_ESP/` → código 6 dígitos |
| Sync eventos | Religar Wi-Fi → heartbeat envia fila |

### 5. Variável importante (.env ou ambiente)

```
ESP32_MODO_SIMULACAO=0
APP_URL_BASE=http://SEU_IP:15000
```

---

## PRs no GitHub

| PR | Branch | Conteúdo |
|----|--------|----------|
| [#5](https://github.com/sandrodemoraes/eleva-locker/pull/5) | `cursor/fase-5-escala-c05c` | PostgreSQL, multi-site, API, BI |
| [#6](https://github.com/sandrodemoraes/eleva-locker/pull/6) | `cursor/esp32-offline-sync-c05c` | ESP offline + sync (inclui fase-5) |

**Use a branch `cursor/esp32-offline-sync-c05c`** — é a mais atual.

---

## Documentação relacionada

- `docs/ESP32_SYNC.md` — protocolo ESP ↔ servidor  
- `docs/VISAO_MUNDIAL.md` — roadmap para ser referência mundial  
- `docs/PROJETO.md` — documento mestre  

---

## Próximos passos sugeridos (quando voltar)

1. Executar comandos acima  
2. Gravar firmware e testar GPIO16  
3. Me avisar resultado (print Serial Monitor + painel ESP online)  
4. Decidir prioridade do roadmap (Fase 6+) em `docs/VISAO_MUNDIAL.md`  

---

## Mensagem para retomar no Cursor

> "Voltei — estou na branch esp32-offline-sync, executei os comandos. [colar resultado do teste ou dúvida]"

Assim continuamos exatamente deste ponto.
