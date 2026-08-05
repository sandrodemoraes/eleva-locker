# ESP32 — Modo offline + sincronização

## Visão geral

| Onde cadastra | O que |
|---------------|-------|
| **Servidor Flask** | Armários, compartimentos, ESP32, encomendas, códigos |
| **ESP32** | Só executa: abre relé, valida código em cache, fila eventos |

A ESP **não cadastra encomendas**. Tudo vem do servidor via sync.

## Fluxo

```
[Servidor sempre ligado]
     │
     │  GET /api/esp32/sync  (compartimentos + códigos ativos)
     ▼
[ESP32 NVS cache] ──offline──► Retirada por código ──► Fila eventos
     │                                              │
     │  POST /api/esp32/eventos (quando Wi-Fi volta) │
     └──────────────────────────────────────────────┘
```

## Cadastro no painel (ordem)

1. **ESP32** → Novo dispositivo  
   - Nome, armário, **max portas** (8–32), token gerado  
2. **Compartimentos** → Para cada porta  
   - Número, relé, **ESP32**, GPIO (opcional), tamanho  
3. **Encomendas** → Depósito no painel  
   - Gera código → incrementa `sync_versao` → ESP puxa no próximo sync  

## API (ESP → Servidor)

| Método | Rota | Função |
|--------|------|--------|
| POST | `/api/esp32/heartbeat` | Online + `precisa_sync` |
| GET | `/api/esp32/sync` | Pacote completo |
| POST | `/api/esp32/eventos` | Upload fila offline |
| POST | `/api/esp32/validar-codigo` | Retirada online |

Header: `X-ESP32-Token: {token}`

## API (Servidor → ESP)

| Método | Rota | Função |
|--------|------|--------|
| GET | `/abrir/{rele}?token=&duracao=3` | Acionar relé |
| GET | `/status?token=` | Teste conexão |
| POST | `/retirar` | Totem local `{codigo}` |

## Firmware

Arquivo: `firmware/elevalocker_sync.ino`

1. Instalar **ArduinoJson 6.x**
2. Editar `WIFI_SSID`, `WIFI_PASSWORD`, `SERVIDOR_URL`, `ESP32_TOKEN`
3. Gravar na ESP32

## Teste sem hardware

```bash
# Terminal 1
python app.py

# Terminal 2 — simulador (só /abrir e /status)
python tools/esp32_simulator.py 8080
```

Cadastre ESP com IP `127.0.0.1`, porta `8080`.

## Variáveis de ambiente (.env)

```
ESP32_MODO_SIMULACAO=0
APP_URL_BASE=http://SEU_IP:15000
ESP32_HEARTBEAT_TIMEOUT=90
ESP32_RELE_DURACAO=3
```
