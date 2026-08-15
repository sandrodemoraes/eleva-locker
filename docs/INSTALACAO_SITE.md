# Instalação ELEVA LOCKER em novo site

Checklist e comparação de arquitetura de rede para ESP32 + servidor + totem.

---

## Como a comunicação funciona

O sistema usa **dois sentidos** na rede local:

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

| Direção | Exemplo | Quem precisa alcançar quem |
|---------|---------|----------------------------|
| ESP → servidor | `GET /api/esp32/sync` | ESP acessa IP do PC |
| Servidor → ESP | `GET http://192.168.x.x/abrir/1` | PC acessa IP da ESP |
| Totem → servidor | `/totem/3`, `/totem/depositar` | Tablet acessa IP do PC |

**Conclusão:** ESP, servidor e totem devem estar na **mesma rede local** (ou na mesma VPN).  
Só colocar URL pública no firmware **não resolve** — o servidor não consegue abrir porta em IP privado atrás de outro roteador.

---

## Comparativo das opções

### Opção A — Servidor local em cada site (recomendada)

```
[Condomínio / Cliente]
  Wi‑Fi "ELEVA - …" ou rede do local
  ├── Roteador 192.168.1.1
  ├── PC ElevaLocker 192.168.1.50:15000  ← servidor
  ├── ESP M1/M2/M3 192.168.1.x
  └── Tablet totem
```

| Prós | Contras |
|------|---------|
| Funciona offline (retirada por código na ESP) | Um PC por site |
| Abertura de porta sempre rápida e confiável | Atualizações em cada PC |
| Sem dependência de internet para abrir porta | Backup/config por site |
| Instalação igual à bancada | |

**Melhor para:** condomínios, lojas, matriz + filiais com armário físico no local.

---

### Opção B — VPN site-a-site (servidor central ELEVA)

```
[Site cliente]                    [Sede ELEVA]
  ESP 192.168.50.x  ◄── VPN ──►  Servidor 192.168.16.130
```

| Prós | Contras |
|------|---------|
| Um servidor central | Configuração de rede/VPN |
| Painel único | Latência maior |
| | Depende de VPN online para abrir porta |
| | TI do cliente precisa cooperar |

**Melhor para:** muitos sites, equipe de TI, necessidade de dashboard centralizado.

---

### Opção C — Só URL pública / internet (não recomendado)

```
ESP ──► http://177.x.x.x:15000  (sync OK)
Servidor ──X──► 192.168.x.x ESP  (abrir porta FALHA)
```

| Prós | Contras |
|------|---------|
| Parece simples | **Abrir porta não funciona** (NAT) |
| | Expõe API na internet |
| | Retirada offline limitada |

**Não usar** como solução principal.

---

## Recomendação ELEVA

| Cenário | Opção |
|---------|--------|
| **1 armário no local** (condomínio, loja) | **A — Servidor local** |
| **Bancada / laboratório** (já feito) | **A** — `192.168.16.130` |
| **Matriz + Bancada na mesma rede** | **A** — mesmo servidor, armários id 2 e 3 |
| **10+ sites com painel central** | **B — VPN** ou A + sync/relatórios futuros |
| **ESP em 4G sem Wi‑Fi local** | Repensar hardware ou gateway local |

**Padrão sugerido:** Opção **A** em cada instalação — mesmo modelo da bancada que já funciona.

---

## Checklist — instalação nova (Opção A)

### Antes de ir ao local

- [ ] PC com Windows, Python, projeto em `C:\ElevaLocker`
- [ ] Backup dos tokens ESP (disco D ou painel) — **um token por placa**
- [ ] Firmware `elevalocker_sync.ino` (~705 linhas) no notebook
- [ ] Cabo USB + driver CP210x (ESP32 Dev)
- [ ] Placa(s) BESTER 8ch testadas na bancada
- [ ] Roteador do local: senha admin, possibilidade de IP fixo (DHCP reservado)

### Rede Wi‑Fi

- [ ] Definir SSID e senha (ex.: `ELEVA - CONDOMINIO X` / senha forte)
- [ ] Anotar faixa de IP do roteador (ex.: `192.168.1.x`)
- [ ] Reservar IP fixo para:
  - [ ] PC servidor (ex.: `.50`)
  - [ ] Cada ESP (ex.: `.121`, `.145`, `.146`)
- [ ] Tablet totem na mesma Wi‑Fi (ou cabo, se aplicável)

### PC servidor

- [ ] Instalar ElevaLocker (`git clone` ou cópia da bancada)
- [ ] `.env` configurado:
  ```env
  ELEVA_BANCADA=1
  DATABASE_URL=
  APP_URL_BASE=http://192.168.1.50:15000
  ELEVA_PAINEL_URL=http://192.168.1.50:15000
  ESP32_MODO_SIMULACAO=0
  TOTEM_ARMARIO_ID=<id do armário>
  NOTIF_MODO=producao
  ```
- [ ] Firewall Windows: liberar porta **15000** (rede privada)
- [ ] `iniciar_elevalocker.bat` + início automático (opcional)
- [ ] Teste: `http://IP_DO_PC:15000/dashboard` de outro celular na mesma rede

### Armário no banco

- [ ] `tools\backup_obrigatorio.bat`
- [ ] Cadastrar armário no painel (ou `cadastrar_esp_nova.py`)
- [ ] 24 portas: 3× ESP com `--porta-inicial 1`, `9`, `17`
- [ ] `tools\configurar_bancada_24_portas.bat` (ajustar `--armario-id`)
- [ ] `tools\diagnostico_reles_bancada.py --corrigir`
- [ ] Diagnóstico: 24 compartimentos **OK**

### Firmware ESP (cada placa)

- [ ] Wi‑Fi e `SERVIDOR_URL` no topo do `.ino`:
  ```cpp
  const char* WIFI_SSID     = "ELEVA - ...";
  const char* WIFI_PASSWORD = "...";
  const char* SERVIDOR_URL  = "http://192.168.1.50:15000";
  const char* ESP32_TOKEN   = "<token do cadastro>";
  const bool RELE_ATIVO_LOW = false;  // Dev — true se C3/BESTER
  ```
- [ ] Upload **uma placa por vez** (COM USB)
- [ ] Serial Monitor 115200: Wi‑Fi OK + `Sync OK`
- [ ] Painel: ESP **online** (verde)

### Validação física

- [ ] `tools\validar_portas_bancada.py --amostra` (#1, #9, #17)
- [ ] `tools\validar_portas_bancada.py --sensores`
- [ ] Totem: `/totem/<id>` — depósito teste + retirada
- [ ] WhatsApp: código recebido (se produção)

### Entrega / documentação no disco D

Salvar pasta por site, ex.: `D:\ElevaLocker\Sites\Condominio-X\`

```
tokens.txt          ← token + IP + nome de cada ESP
rede.txt            ← SSID, IP servidor, IPs ESP
.env.backup         ← cópia do .env (sem senhas se preferir)
fotos/              ← armário, placas, roteador (opcional)
```

---

## Checklist — migrar armário para outra rede

Se mudar de prédio/rede (novo Wi‑Fi, novo IP):

1. [ ] Novo IP fixo no roteador (servidor + ESPs)
2. [ ] Atualizar `.env`: `APP_URL_BASE` e `ELEVA_PAINEL_URL`
3. [ ] Regravar **todas** as ESPs: `WIFI_SSID`, `WIFI_PASSWORD`, `SERVIDOR_URL`
4. [ ] **Tokens podem permanecer iguais** (se o banco for o mesmo)
5. [ ] Reiniciar servidor
6. [ ] Teste heartbeat no painel + `--amostra`

---

## Comandos úteis (referência bancada)

```cmd
cd /d C:\ElevaLocker
tools\backup_obrigatorio.bat
tools\configurar_bancada_24_portas.bat
py tools\diagnostico_reles_bancada.py --corrigir
py tools\validar_portas_bancada.py --amostra
tools\atualizar_totens.bat
py tools\corrigir_tokens_bancada.py --listar
```

---

## Decisão rápida (perguntas)

| Pergunta | Se SIM → | Se NÃO → |
|----------|----------|----------|
| Há PC Windows no local do armário? | Opção **A** | Levar mini-PC ou Opção **B** |
| ESP e PC na mesma Wi‑Fi? | Seguir checklist | Ajustar rede primeiro |
| Cliente exige painel só na sede? | Estudar **VPN (B)** | **A** com acesso remoto ao PC (TeamViewer) |
| Só 1 armário 8 portas? | **A** com 1 ESP | — |
| 24 portas (3 placas)? | **A** — modelo bancada | — |

---

## Próximo passo sugerido

1. Confirmar **Opção A** para o primeiro cliente fora da bancada.
2. Montar **kit de instalação** (PC + 3 ESP + roteador dedicado opcional).
3. Testar em laboratório simulando “rede do cliente” (outro SSID / faixa 192.168.1.x).

Documentos relacionados: [SETUP_OFICIAL.md](SETUP_OFICIAL.md), [ESP32_SYNC.md](ESP32_SYNC.md), [TOTEM_TABLET_KIOSK.md](TOTEM_TABLET_KIOSK.md).
