# Teste de bancada — ESP32 + ELEVA LOCKER (8 relés)

> Seu hardware: ESP32 + placa BESTER 8 canais | IP ESP: **192.168.16.162**

---

## Visão geral

```
[Cadastro no PC — ELEVA LOCKER]
  Usuários, Armário, ESP32, 8 Compartimentos, Encomendas
              │
              │  sync + abrir relé
              ▼
[ESP32 — firmware elevalocker_sync.ino]
  8 relés GPIO 16,17,18,19,21,22,23,27
```

**Usuários** cadastram no painel → **Encomendas** no painel → **ESP** só abre portas e valida códigos.

---

## PARTE 1 — PC (servidor)

### 1.1 Atualizar código
```powershell
cd C:\ElevaLocker
git fetch origin
git checkout cursor/esp32-offline-sync-c05c
git pull origin cursor/esp32-offline-sync-c05c
pip install -r requirements.txt
```

### 1.2 Descobrir IP do PC
```powershell
ipconfig
```
Anote o IPv4 (ex: **192.168.16.130**)

### 1.3 Configurar bancada automaticamente
```powershell
python tools/setup_bancada.py --ip-esp 192.168.16.162
```

Isso cria:
- Armário **Bancada Teste**
- ESP **ESP Bancada 8ch** com IP 192.168.16.162
- **8 compartimentos** (relé 1–8, GPIOs corretos)

**Copie o TOKEN** que aparecer no terminal.

### 1.4 Subir servidor
```powershell
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
python app.py
```

Troque `192.168.16.130` pelo IP do seu PC.

### 1.5 Cadastrar usuário (se quiser operador de teste)

1. http://localhost:15000/usuarios  
2. **Novo usuário** → ex: `Operador Bancada` / email / senha / perfil Operador  

*(Admin `sandro.demoraes@gmail.com` também funciona.)*

---

## PARTE 2 — ESP32 (firmware integrado)

### 2.1 Arduino IDE

1. Biblioteca **ArduinoJson 6.x**  
2. Abrir `firmware/elevalocker_sync.ino`  
3. Editar:

```cpp
const char* WIFI_SSID     = "ELEVA - ENERGIA SOLAR";
const char* WIFI_PASSWORD = "eleva2277";   // sua senha real

const char* SERVIDOR_URL  = "http://192.168.16.130:15000";  // IP do PC
const char* ESP32_TOKEN   = "TOKEN_DO_SETUP_BANCADA";       // colar aqui
```

4. **Upload** na ESP32  
5. Serial Monitor **115200** → deve mostrar:
   - WiFi conectado  
   - IP (192.168.16.162)  
   - `Sync OK v1 — 8 compartimentos`

### 2.2 Tela da ESP (nova)

Abrir http://192.168.16.162/

Deve aparecer **ELEVA LOCKER ESP** (não "Armário Inteligente").

---

## PARTE 3 — Testes na bancada

### Teste A — Relés pelo painel

1. http://localhost:15000/esp32/bancada  
2. Clicar **Abrir relé 1** … até **relé 8**  
3. Cada clique = relé correspondente  

### Teste B — ESP online no painel

1. http://localhost:15000/esp32  
2. Status deve ficar **online** (heartbeat ~30s)  
3. Botão Wi-Fi **Testar** → sucesso  

### Teste C — Depósito + retirada (fluxo real)

1. **Encomendas** → Depositar → compartimento **#3** → cliente teste  
2. Anotar **código 6 dígitos**  
3. Relé 3 deve abrir no depósito  
4. Retirar:
   - **Online:** totem http://localhost:15000/totem ou ESP http://192.168.16.162/  
   - Digitar código → relé 3 abre de novo  

### Teste D — Offline

1. Desligar Wi-Fi do roteador (PC e ESP ficam na mesma rede sem internet externa — ou desconectar ESP do AP por 2 min usando modo teste)  
   - *Mais simples:* desligar só o **PC** por 1 min, depositar código antes, retirar na ESP offline  
2. Na ESP: digitar código → relé abre  
3. Ligar PC de novo → ESP envia evento → encomenda marcada retirada no painel  

---

## Checklist

```
[ ] setup_bancada.py executado
[ ] Token no firmware
[ ] Firmware elevalocker_sync gravado (não o antigo)
[ ] Serial: Sync OK 8 compartimentos
[ ] /esp32/bancada — 8 relés clicam
[ ] Depósito encomenda → código gerado
[ ] Retirada por código na ESP
[ ] ESP online no painel
```

---

## Problemas comuns

| Problema | Solução |
|----------|---------|
| Ainda aparece "Armário Inteligente" | Firmware antigo — gravar `elevalocker_sync.ino` |
| ESP offline no painel | Token errado ou SERVIDOR_URL errado |
| Relé não clica pelo painel | `ESP32_MODO_SIMULACAO=0`, IP ESP correto no cadastro |
| Sync 0 compartimentos | Rodar `setup_bancada.py` de novo |
| Token inválido | Token do painel = token do .ino (sem espaços) |

---

## URLs úteis

| URL | Função |
|-----|--------|
| http://localhost:15000/esp32/bancada | Teste relés |
| http://localhost:15000/esp32 | Cadastro ESP |
| http://localhost:15000/encomendas | Depósito/retirada |
| http://192.168.16.162/ | Totem na ESP |

---

Quando terminar, me envie print do Serial Monitor + tela `/esp32/bancada`.
