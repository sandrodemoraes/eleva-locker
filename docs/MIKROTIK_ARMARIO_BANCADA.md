# MikroTik armário — teste na bancada (2ª internet)

Simula instalação em cliente: **hub sede** (RB ELEVA 1) + **spoke armário** (2º MikroTik + outra internet).

## Topologia

```
[Internet 1 — sede]                    [Internet 2 — bancada simula cliente]
     │                                              │
     ▼                                              ▼
RB ELEVA 1 (hub)                              MikroTik armário (spoke)
192.168.16.100                                WAN = DHCP internet 2
wg-eleva 10.255.0.1                           LAN/Wi-Fi 192.168.50.0/24
     │                                              │
     └──────── WireGuard UDP 51820 ────────────────┘
                    (spoke inicia conexão)

PC Flask 192.168.16.130 ──via hub──► ESPs 192.168.50.121 / .145 / .146
```

**Importante:** no spoke, `endpoint-address` = **IP público da internet 1** (sede), não `192.168.16.100`.

---

## Pré-requisitos

### Hub (RB ELEVA 1) — já feito
- [x] ROS 7.21.5
- [x] wg-eleva, 10.255.0.1/24, UDP 51820
- [x] Public Key hub: ver `D:\mikrotik\wg-keys.txt`

### Sede — internet 1
- [ ] Anotar **IP público** (ex.: https://ifconfig.me no PC da rede 16.x)
- [ ] **Port forward:** UDP **51820** → **192.168.16.100**

### Armário — 2º MikroTik
- [ ] ROS **7.x** (upgrade igual ao hub se estiver em v6)
- [ ] Cabo WAN → roteador da **internet 2**
- [ ] Cabo LAN ou Wi‑Fi para ESPs

---

## Parte A — Preparar MikroTik armário

### A1. Backup
```
/export file=armario-pre-config
```
Download → `D:\mikrotik\`

### A2. Upgrade ROS 7 (se necessário)
System → Packages → Channel **upgrade** → Download & Install

### A3. WAN (internet 2)
Conecte **ether1** (ou porta WAN) na outra internet.

Quick Set ou DHCP client na WAN — confirme internet:
```
/ping 8.8.8.8 count=3
```

### A4. LAN armário — 192.168.50.0/24

Ajuste `ether2` se usar outra porta:

```
/interface bridge add name=bridge-armario
/interface bridge port add bridge=bridge-armario interface=ether2
/ip address add address=192.168.50.1/24 interface=bridge-armario
/ip pool add name=pool-armario ranges=192.168.50.120-192.168.50.200
/ip dhcp-server add name=dhcp-armario interface=bridge-armario address-pool=pool-armario
/ip dhcp-server network add address=192.168.50.0/24 gateway=192.168.50.1 dns-server=192.168.50.1
```

Reservas ESP (substituir MACs reais quando souber):

```
/ip dhcp-server lease add address=192.168.50.121 mac-address=AA:BB:CC:DD:EE:01 comment="ESP M1"
/ip dhcp-server lease add address=192.168.50.145 mac-address=AA:BB:CC:DD:EE:02 comment="ESP M2"
/ip dhcp-server lease add address=192.168.50.146 mac-address=AA:BB:CC:DD:EE:03 comment="ESP M3"
```

### A5. Wi‑Fi (se hAP — ROS 7)

Via WinBox **WiFi** → nova rede ou Quick Set:
- SSID: `ELEVA - LOCKER BANCADA`
- Senha: (anotar para firmware ESP)
- Bridge: `bridge-armario`

---

## Parte B — WireGuard no armário (spoke)

Substituir `IP_PUBLICO_SEDE` pelo IP público da internet 1:

```
/interface wireguard add name=wg-sede listen-port=51821 mtu=1420
/ip address add address=10.255.0.50/32 interface=wg-sede
/interface wireguard peers add interface=wg-sede \
  public-key="pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU=" \
  endpoint-address=IP_PUBLICO_SEDE \
  endpoint-port=51820 \
  allowed-address=10.255.0.0/24,192.168.16.0/24 \
  persistent-keepalive=25s \
  comment="Hub RB ELEVA 1"
/ip route add dst-address=192.168.16.130/32 gateway=10.255.0.1
/ip firewall filter add chain=forward action=accept comment="VPN ELEVA" place-before=0
```

Copiar **Public Key do armário**:
```
/interface wireguard print detail
```

Salvar em `D:\mikrotik\wg-keys.txt` como `ARMARIO_PUBLIC_KEY=...`

---

## Parte C — Peer no hub (RB ELEVA 1)

No **RB ELEVA 1**, substituir `CHAVE_PUBLICA_ARMARIO`:

```
/interface wireguard peers add interface=wg-eleva \
  public-key="CHAVE_PUBLICA_ARMARIO" \
  allowed-address=10.255.0.50/32,192.168.50.0/24 \
  comment="Locker-bancada-teste"
/ip route add dst-address=192.168.50.0/24 gateway=10.255.0.50
/ip firewall filter add chain=forward src-address=192.168.50.0/24 dst-address=192.168.16.130 action=accept comment="Armario->Flask"
/ip firewall filter add chain=forward src-address=192.168.16.130 dst-address=192.168.50.0/24 action=accept comment="Flask->ESPs"
```

---

## Parte D — ESPs

Firmware (cada placa no armário):

```cpp
const char* WIFI_SSID     = "ELEVA - LOCKER BANCADA";
const char* WIFI_PASSWORD = "...";
const char* SERVIDOR_URL  = "http://192.168.16.130:15000";
```

Painel → cadastrar ESPs com IP **192.168.50.121 / .145 / .146** (não 192.168.16.x).

---

## Parte E — Testes

### No RB ELEVA 1 (hub)
```
/interface wireguard peers print
/ping 10.255.0.50 count=5
/ping 192.168.50.121 count=5
```
Peers devem mostrar **RX/TX** aumentando.

### No PC Flask (192.168.16.130)
```
ping 192.168.50.121
py tools\validar_portas_bancada.py --amostra
```

### Painel
- ESPs **online**
- Abrir compartimento funciona

---

## Checklist disco D

```
D:\mikrotik\
  wg-keys.txt              ← hub + armário public keys
  eleva-pos-ros7-wg-hub.rsc
  armario-bancada.rsc
  rede.txt
```

### rede.txt (modelo)

```
HUB sede: RB ELEVA 1, 192.168.16.100
Hub WG pubkey: pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU=
IP publico sede: ___.___.___.___ 
Port forward: UDP 51820 -> 192.168.16.100

ARMARIO bancada teste:
WG IP: 10.255.0.50
LAN: 192.168.50.0/24
ESPs: .121 .145 .146
SSID: ELEVA - LOCKER BANCADA
Armario WG pubkey: (preencher)

Flask: http://192.168.16.130:15000
```

---

## Problemas comuns

| Sintoma | Causa | Solução |
|---------|-------|---------|
| Peer sem RX/TX | Port forward 51820 | Conferir roteador internet 1 |
| Ping 10.255.0.50 ok, .121 falha | Rota/firewall hub | Rotas + filter forward |
| ESP offline | IP errado no painel | IPs 192.168.50.x |
| endpoint errado | IP privado no spoke | Usar IP **público** sede |

Documento hub: [MIKROTIK_VPN_HUB.md](MIKROTIK_VPN_HUB.md)
