# Sensor de porta — bancada (compartimento 1)

> Fechadura eletromagnética 12 V com **2 fios de sensor**.  
> Comportamento confirmado pelo usuário:

| Estado da porta | Sensor (2 fios) | Leitura lógica |
|-----------------|-----------------|----------------|
| **Fechada** | Curto (continuidade) | Porta fechada |
| **Aberta** | Aberto (sem continuidade) | Porta aberta |

Tipo: **NC em repouso com porta fechada** (switch fecha quando a porta trava).

---

## Fiação

### Fechadura (4 fios no total)

| Fios | Função | Ligação |
|------|--------|---------|
| Vermelho + preto | Solenoide 12 V | Placa relés BESTER (relé 1 / GPIO 16) |
| Amarelo + preto *(ou 2 fios do sensor)* | Sensor porta | GPIO input ESP32 |

### Sensor → ESP32

```
Fio sensor A  ──► GPIO 32
Fio sensor B  ──► GND ESP32
```

- Modo: `INPUT_PULLUP` (pull-up interno ~45 kΩ)
- **Porta fechada** → fios em curto → GPIO lido **LOW**
- **Porta aberta** → fios abertos → pull-up → GPIO lido **HIGH**

### GND comum

A **fonte 12 V (−)** e o **GND da ESP32** devem estar no mesmo referencial.

---

## Lógica no firmware

```cpp
#define SENSOR_GPIO_PORTA_1  32

pinMode(SENSOR_GPIO_PORTA_1, INPUT_PULLUP);

bool portaFechada() {
  return digitalRead(SENSOR_GPIO_PORTA_1) == LOW;
}

bool portaAberta() {
  return digitalRead(SENSOR_GPIO_PORTA_1) == HIGH;
}
```

Endpoint previsto:

```
GET /sensor/1?token=SEU_TOKEN
```

Resposta:

```json
{
  "rele": 1,
  "fechada": true,
  "aberta": false,
  "sensor": true
}
```

---

## Mapa GPIO (placa BESTER 8ch)

| Compartimento | Relé (saída) | Sensor (entrada) — bancada |
|---------------|--------------|----------------------------|
| 1 | GPIO 16 | **GPIO 32** (teste) |
| 2 | GPIO 17 | GPIO 33 *(futuro)* |
| 3 | GPIO 18 | GPIO 34 *(futuro)* |
| … | … | … |

**Não usar GPIO 25.**

GPIO 34–39 são input-only (sem pull-up interno forte) — preferir **32, 33** para sensores com pull-up externo se necessário.

---

## Teste na bancada (checklist)

### 1. Multímetro (sem ESP)

- [ ] Porta fechada → continuidade entre os 2 fios do sensor
- [ ] Porta aberta → **sem** continuidade

### 2. Só ESP + sensor (relé desligado)

- [ ] Serial Monitor: fechada = `LOW`, aberta = `HIGH`
- [ ] Debounce: ler 3× com 50 ms entre leituras (evitar ruído)

### 3. Relé + fechadura

- [ ] `GET /abrir/1` → solenoide destrava
- [ ] Sensor muda para aberta (HIGH)
- [ ] Fechar porta → sensor volta fechada (LOW)

### 4. Totem (depósito)

- [ ] Depositar → compartimento 1 abre
- [ ] Tela “Porta aberta”
- [ ] Fechar fisicamente → em ~2 s totem conclui **sem botão**
- [ ] WhatsApp enviado

---

## Fluxo software (já previsto no totem v2)

```
Totem deposita → abre relé
       ↓
Poll GET /totem/porta/{id}/status  (a cada 2 s)
       ↓
Servidor consulta ESP GET /sensor/{rele}
       ↓
fechada == true  →  POST concluir depósito  →  WhatsApp
```

Hoje o endpoint do servidor retorna stub (`sensor: false`). Implementação: firmware `/sensor/1` + Flask consultando ESP.

---

## Segurança

- **Nunca** ligar 12 V / 24 V do solenoide nos GPIO da ESP
- Sensor é **contato seco** — OK direto no GPIO + GND
- Cabo do sensor longe dos fios de potência do relé (ruído)

---

## Próximo passo no código

1. Firmware: leitura GPIO 32 + endpoint `/sensor/{rele}`
2. `esp32.py`: método `ler_sensor(ip, rele)`
3. `routes/totem.py`: `status_porta` com dado real
4. Teste bancada compartimento 1
