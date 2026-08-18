# ELEVA LOCKER — Portas do armário (8 a 64)

Pasta com atalhos e comandos para expandir um armário usando módulos **ESP32 + placa BESTER 8ch**.

> **Padrão:** armário **id=2** — edite `tools/portas/_config.bat` se o seu for outro.

---

## Início rápido (Windows)

```cmd
cd C:\ElevaLocker
tools\portas\menu.bat
```

Ou clique duplo em `tools\portas\menu.bat`.

---

## Arquivos

| Arquivo | Função |
|---------|--------|
| `menu.bat` | Menu principal |
| `_config.bat` | **ARMARIO_ID**, servidor, IPs sugeridos |
| `configurar_08.bat` … `configurar_64.bat` | Sincroniza compartimentos no banco |
| `cadastrar_modulo.bat` | Cadastra ESP M1–M8 no painel |
| `validar.bat` | Lista mapeamento e testa relés |
| `listar_armarios.bat` | Mostra ids dos armários |
| `COMANDOS.txt` | Comandos CMD para copiar/colar |

---

## Regra de hardware

| Portas | ESPs (8 relés) | Compartimentos |
|--------|----------------|----------------|
| 8 | 1 | #1 – #8 |
| 16 | 2 | #1 – #16 |
| 24 | 3 | #1 – #24 |
| 32 | 4 | #1 – #32 |
| 64 | 8 | #1 – #64 |

Cada ESP controla **relés locais 1–8**. O número do compartimento no painel é global (#9 = relé 1 da 2ª placa).

---

## Fluxo recomendado

1. **Painel** → Editar armário → quantidade de portas (8/16/24/32/64)
2. **`configurar_XX.bat`** → alinha compartimentos das ESPs já cadastradas
3. **`cadastrar_modulo.bat`** → cadastra ESP que falta (imprime **TOKEN**)
4. **Arduino** → gravar `firmware/elevalocker_sync/elevalocker_sync.ino` com token de cada placa
5. **`validar.bat`** → conferir mapeamento e testar abertura

---

## Painel e totem

Substitua `2` pelo seu `ARMARIO_ID`:

- Armário: `http://192.168.16.130:15000/armarios/2`
- Totem: `http://192.168.16.130:15000/totem/2`

---

## Firmware (todas as placas)

Arquivo: `firmware/elevalocker_sync/elevalocker_sync.ino`

```cpp
const char* WIFI_SSID     = "ELEVA - ENERGIA SOLAR";
const char* WIFI_PASSWORD = "eleva2277";
const char* SERVIDOR_URL  = "http://192.168.16.130:15000";
const char* ESP32_TOKEN   = "TOKEN_DO_PAINEL";  // um token por placa
const bool RELE_ATIVO_LOW = true;
```

Biblioteca: **ArduinoJson 6.x**

---

## Script Python (alternativa ao .bat)

```cmd
py tools\configurar_portas_armario.py --armario-id 2 --portas 16
py tools\configurar_portas_armario.py --listar
```

Comandos detalhados por módulo: **`COMANDOS.txt`**
