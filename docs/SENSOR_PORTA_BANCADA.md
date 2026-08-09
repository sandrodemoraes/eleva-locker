# Sensor de porta — 8 compartimentos (BESTER 8ch)

> Fechadura 12 V com **2 fios de sensor** (NC).  
> **Porta fechada** = fios em curto → GPIO **LOW**  
> **Porta aberta** = fios abertos → GPIO **HIGH** (`INPUT_PULLUP`)

---

## Mapa GPIO — relé × sensor

| Porta | Relé (12 V) | GPIO relé | GPIO sensor |
|-------|-------------|-----------|-------------|
| 1 | 1 | 16 | **32** |
| 2 | 2 | 17 | **33** |
| 3 | 3 | 18 | **12** |
| 4 | 4 | 19 | **13** |
| 5 | 5 | 21 | **14** |
| 6 | 6 | 22 | **15** |
| 7 | 7 | 23 | **26** |
| 8 | 8 | 27 | **4** |

**Não usar GPIO 25.**

### Fiação de cada fechadura

| Fios | Ligação |
|------|---------|
| Vermelho + preto | Placa relés (mesmo relé da porta) |
| Sensor (2 fios) | GPIO sensor da porta → **GND** comum |

**GND** da fonte 12 V = **GND** da ESP32.

---

## Firmware (v2.4+)

Gravar: `firmware/elevalocker_sync.ino`

Endpoints:

```
GET /sensor/1?token=...     → uma porta
GET /sensores?token=...     → todas as 8
```

Resposta:

```json
{"rele":1,"gpio":32,"fechada":true,"aberta":false,"sensor":true}
```

Painel local ESP: `http://IP_ESP/` mostra **Porta: FECHADA/ABERTA** por compartimento.

---

## Servidor + totem (v2.4.0)

```
GET /totem/porta/{compartimento_id}/status
→ consulta ESP /sensor/{rele}
→ fechada:true → totem conclui depósito + WhatsApp
```

---

## Teste na bancada

### 1. Gravar firmware

Arduino IDE → ESP32 → `elevalocker_sync.ino` → Upload

### 2. Testar sensores pelo PC

```cmd
cd C:\ElevaLocker
python tools/testar_sensores.py --esp 192.168.16.162 --token SEU_TOKEN
```

Uma porta:

```cmd
python tools/testar_sensores.py --esp 192.168.16.162 --token SEU_TOKEN --rele 1
```

Via banco (compartimento id):

```cmd
python tools/testar_sensores.py --compartimento 5
```

### 3. Testar no navegador

```
http://192.168.16.162/sensor/1?token=SEU_TOKEN
http://192.168.16.162/sensores?token=SEU_TOKEN
http://192.168.16.162/?token=SEU_TOKEN
```

### 4. Testar totem

1. Depositar → porta abre  
2. Fechar fisicamente → totem detecta em ~2 s  
3. WhatsApp automático  

### 5. Simulador (sem hardware)

```cmd
python tools/esp32_simulator.py 8080
python tools/testar_sensores.py --esp 127.0.0.1 --token eleva-esp32-token-2026
```

Simular fechar porta 1: `http://127.0.0.1:8080/sensor/1/fechar?token=eleva-esp32-token-2026`

---

## Checklist instalação (8 portas)

- [ ] 8 fechaduras 12 V fioadas (verm/preto nos relés)
- [ ] 8 pares sensor → GPIO 32,33,12,13,14,15,26,4 + GND
- [ ] Multímetro: fechada=curto, aberta=aberto (cada porta)
- [ ] Firmware gravado
- [ ] `/sensores` mostra 8 portas corretas
- [ ] Totem depósito + fechar → WhatsApp OK

---

## Problemas comuns

| Sintoma | Causa provável |
|---------|----------------|
| Sempre ABERTA | Sensor não conectado ou fio solto (pull-up = HIGH) |
| Sempre FECHADA | Curto permanente no GPIO |
| Totem não conclui | ESP sem IP / token errado / firmware antigo |
| GPIO 4 instável | Usar cabo curto; evitar ruído dos relés |
