# Instalação ELEVA LOCKER — site piloto (Modelo A)

**Para:** Sandro / ELEVA  
**Objetivo:** Começar a testar um site remoto com **servidor local no condomínio** — operação offline-first, WireGuard só para gestão Matriz.

Documento relacionado: [ARQUITETURA_REDE_FASES.md](ARQUITETURA_REDE_FASES.md)

---

## Começar agora (3 caminhos)

| Caminho | Quando usar | Comando |
|---------|-------------|---------|
| **A — Piloto na bancada** | Testar fluxo site sem ir ao cliente | Na Matriz, criar site no banco e simular com armário id 3 |
| **B — Mini PC no local** | 1º cliente / condomínio real | PC no site + `.env` local |
| **C — WireGuard depois** | Matriz enxergar site remoto | Só após A ou B funcionarem na LAN |

### Passo 1 — Criar site no banco (qualquer caminho)

Na Matriz ou no PC do site (primeira execução):

```cmd
cd /d C:\ElevaLocker
py tools\bootstrap_site_piloto.py ^
  --nome "Condomínio Piloto 050" ^
  --codigo piloto-050 ^
  --cidade "Lauro Müller" ^
  --estado SC ^
  --endereco "Rua Exemplo, 100" ^
  --portas 16 ^
  --ip-servidor 192.168.50.10 ^
  --gerar-api-key
```

Isso cria:

- Registro em **Sites** no painel (`/sites`)
- Armário vinculado ao site
- Pasta `Sites\piloto-050\` com `env.txt`, `rede.txt` e opcionalmente `api_key.txt`

### Passo 2 — Configurar PC do site

```cmd
copy Sites\piloto-050\env.txt .env
REM ou: py tools\criar_env_site.py --ip 192.168.50.10 --armario-id 3 --codigo piloto-050
INICIAR.bat
```

Abrir: `http://192.168.50.10:15000/dashboard`

### Passo 3 — ESP e totem (mesma LAN)

Firmware (`elevalocker_sync.ino`):

```cpp
const char* SERVIDOR_URL  = "http://192.168.50.10:15000";  // IP LOCAL do site
const char* ESP32_TOKEN   = "<token de Sites/piloto-050/rede.txt>";
```

Totem Fully:

```
http://192.168.50.10:15000/totem/<armario_id>?kiosk=1
```

---

## Como a comunicação funciona

```
┌─────────────┐   heartbeat / sync / eventos    ┌──────────────────┐
│  ESP32 × N  │ ──────────────────────────────► │  PC Servidor     │
│  (placas)   │ ◄────────────────────────────── │  Flask :15000    │
└─────────────┘   abrir relé / ler sensor       └────────┬─────────┘
                                                          │
                                                   ┌──────▼──────┐
                                                   │ Totem/tablet │
                                                   └─────────────┘
```

| Direção | Exemplo | Quem alcança quem |
|---------|---------|-------------------|
| ESP → servidor | `GET /api/esp32/sync` | ESP acessa IP **local** do PC |
| Servidor → ESP | `GET http://192.168.x.x/abrir/1` | PC acessa IP da ESP na LAN |
| Totem → servidor | `/totem/3`, depósito | Tablet na mesma rede |

**Regra:** ESP, servidor e totem na **mesma rede local**.  
`SERVIDOR_URL` aponta para o **PC do site**, não para a Matriz.

---

## Modelo A vs WireGuard

| Plano | O quê | Precisa internet? | Precisa WG? |
|-------|--------|-------------------|-------------|
| **Operacional** | Totem, ESP, retirada | ❌ | ❌ |
| **Notificação** | WhatsApp | ✅ | ❌ |
| **Gestão** | Matriz ver site remoto | ✅ | ✅ |

WireGuard **não substitui** o servidor local — só permite a Matriz acessar o painel do site quando online.

---

## Teste na bancada (antes do cliente)

Simular site remoto **na mesma rede da Matriz**:

1. `bootstrap_site_piloto.py` com `--ip-servidor 192.168.16.130` (ou outro IP reservado)
2. Criar armário “Piloto 050” (site_id ≠ Matriz)
3. ESP de teste com `SERVIDOR_URL` local
4. Validar depósito + retirada + offline (desligar internet, manter LAN)

Matriz continua com armário id=2; piloto usa outro id — **dois sites no mesmo PC** é válido para teste de painel multi-site.

Para **produção em campo**, cada site deve ter **PC + banco próprios** (Modelo A).

---

## Checklist — instalação no local (Modelo A)

### Antes de ir

- [ ] PC Windows + Python + `C:\ElevaLocker`
- [ ] `bootstrap_site_piloto.py` executado (ou site criado no painel)
- [ ] Tokens ESP anotados em `Sites\<codigo>\rede.txt`
- [ ] Firmware no notebook + cabo USB

### Rede

- [ ] SSID/senha definidos (ex.: `ELEVA - PILOTO 050`)
- [ ] IP fixo reservado: PC servidor (ex. `.10`), cada ESP (ex. `.121`, `.145`)
- [ ] Tablet totem na mesma Wi‑Fi

### PC servidor

- [ ] `.env` com `APP_URL_BASE=http://IP_LOCAL:15000`
- [ ] `ESP32_MODO_SIMULACAO=0`
- [ ] Firewall: porta **15000** rede privada
- [ ] `INICIAR.bat` OK — dashboard acessível de outro celular na LAN

### Armário

- [ ] ESPs cadastradas no painel
- [ ] 24 portas: 3× ESP (`--porta-inicial 1`, `9`, `17`) se aplicável
- [ ] `validar_portas_bancada.py --amostra` OK

### Validação

- [ ] Painel: ESP **online** (verde)
- [ ] Totem: depósito + retirada
- [ ] **Teste offline:** desligar internet WAN — totem + ESP continuam na LAN
- [ ] WhatsApp (se Evolution no site ou na Matriz via rede)

### Pasta por site (`Sites\<codigo>\`)

```
env.txt       ← snippet .env
rede.txt      ← IPs, tokens, URL totem
api_key.txt   ← monitoramento Matriz (opcional)
tokens.txt    ← backup manual tokens
fotos/        ← opcional
```

---

## WireGuard — fase 2 do piloto

Só depois da operação local OK:

1. Peer no HUB Matriz — ver [WIREGUARD_PEERS.md](WIREGUARD_PEERS.md)
2. Matriz acessa painel: `http://10.255.0.50:15000` (IP WG do site)
3. Monitoramento: `GET /api/v1/status` + `X-API-Key` (gerado com `--gerar-api-key`)

Guia hub sede: [MIKROTIK_VPN_HUB.md](MIKROTIK_VPN_HUB.md)

---

## Opção B+ — MikroTik dentro do armário (escala)

Para muitos sites com painel centralizado na sede — **não é o piloto recomendado**.

- MikroTik montado **dentro do armário**
- ESP na Wi‑Fi do MikroTik
- VPN WireGuard para sede
- **Atenção:** se ESP apontarem `SERVIDOR_URL` para Matriz via WG, operação depende de internet — ver Modelo B em `ARQUITETURA_REDE_FASES.md`

Piloto: preferir **Modelo A** (PC local). B+ quando padronizar escala.

---

## Comandos úteis

```cmd
cd /d C:\ElevaLocker
INSTALAR_SITE.bat
py tools\bootstrap_site_piloto.py --help
py tools\criar_env_site.py --ip 192.168.50.10 --armario-id 3
tools\instalacao_site_checklist.bat
py tools\validar_portas_bancada.py --amostra
```

---

## Decisão rápida

| Pergunta | SIM | NÃO |
|----------|-----|-----|
| PC no local do armário? | **Modelo A** | Mini-PC ou repensar |
| Testar antes do cliente? | **Bancada** com bootstrap | — |
| Matriz precisa ver remoto? | WG **depois** do piloto local | Só operação local |
| Internet instável? | **Modelo A** obrigatório | Evitar Modelo B |

---

*Atualizado em 02/09/2026 — piloto Modelo A; WireGuard = gestão.*
