# ELEVA LOCKER — Documentação RB Matriz + RB Armário

> **Versão:** 2026-08-17 · Site piloto **050** (bancada)  
> **Salvar cópia Word:** `D:\ELEVA_LOCKER_Documentacao_RB_ARMARIO_RB_MATRIZ.docx`  
> **Exports MikroTik:** `D:\mikrotik\`

---

## 1. Visão geral

```
[Internet 1 — sede]                         [Internet local — armário]
       │                                              │
       ▼                                              ▼
 RB ELEVA 1 (MATRIZ)                          RB-ELEVA-L050 (ARMÁRIO)
 192.168.16.100                               WAN ether1 (DHCP)
 wg-eleva 10.255.0.1                           LAN 192.168.50.0/24
       │                                       wg-sede 10.255.0.50
       └──────── WireGuard UDP 51820 ──────────┘
              (spoke inicia; keepalive 25s)

 PC Flask 192.168.16.130 ── mesma LAN sede ──► via hub VPN ──► ESPs 192.168.50.x
```

| Equipamento | Identity | IP LAN | VPN WireGuard |
|-------------|----------|--------|---------------|
| **Matriz (hub)** | RB ELEVA 1 | `192.168.16.100` | `10.255.0.1/24` |
| **Armário (spoke)** | RB-ELEVA-L050 | `192.168.50.1/24` | `10.255.0.50/32` |
| **Servidor Flask** | PC sede | `192.168.16.130` | — (mesma LAN da matriz) |

**Importante:** o Flask **não passa** pelo MikroTik — fica no mesmo roteador da sede (`192.168.16.x`). O hub só **encaminha** tráfego VPN ↔ Flask.

---

## 2. Chaves WireGuard (site 050)

| Papel | Interface | Public Key |
|-------|-----------|------------|
| **Matriz** | `wg-eleva` | `pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU=` |
| **Armário** | `wg-sede` | `hxGlOG+QVgTEkMWJSPuXY4Uefkkr+6CcfohTBq6HuGA=` |

Salvar também em `D:\mikrotik\wg-keys.txt`.

**Regra:** no **hub**, o peer usa a chave **do armário**. No **armário**, o peer usa a chave **da matriz**.

---

## 3. Rede sede (matriz)

| Item | Valor |
|------|--------|
| Modelo | MikroTik hEX (RB750Gr3) |
| RouterOS | 7.21.5 (long-term) |
| IP fixo LAN | `192.168.16.100/24` (interface `ether1 ATEKI`) |
| IP público sede | `177.74.79.32` |
| Port forward | **UDP 51820** → `192.168.16.100` |
| WireGuard listen | **UDP 51820** (`wg-eleva`) |

### 3.1 WireGuard hub

```
/interface wireguard add name=wg-eleva listen-port=51820 mtu=1420
/ip address add address=10.255.0.1/24 interface=wg-eleva
```

### 3.2 Peer armário L050

```
/interface wireguard peers add interface=wg-eleva \
  public-key="hxGlOG+QVgTEkMWJSPuXY4Uefkkr+6CcfohTBq6HuGA=" \
  allowed-address=10.255.0.50/32,192.168.50.0/24 \
  comment="RB-ELEVA-L050"
```

### 3.3 Rota LAN armário

```
/ip route add dst-address=192.168.50.0/24 gateway=10.255.0.50
```

### 3.4 Firewall mínimo (matriz)

```
/ip firewall filter add chain=input protocol=udp dst-port=51820 action=accept comment="WireGuard armarios"
/ip firewall filter add chain=input in-interface=wg-eleva action=accept place-before=0 comment="VPN input"
/ip firewall filter add chain=forward in-interface=wg-eleva action=accept place-before=0 comment="VPN in"
/ip firewall filter add chain=forward out-interface=wg-eleva action=accept place-before=0 comment="VPN out"
/ip firewall filter add chain=forward src-address=192.168.50.0/24 dst-address=192.168.16.0/24 action=accept place-before=0 comment="Armario->Sede"
/ip firewall filter add chain=forward src-address=192.168.16.0/24 dst-address=192.168.50.0/24 action=accept place-before=0 comment="Sede->Armario"
/ip firewall filter add chain=forward action=accept connection-state=established,related,untracked place-before=0
```

---

## 4. Rede armário (spoke)

| Item | Valor |
|------|--------|
| Identity | `RB-ELEVA-L050` |
| WAN | `ether1` — **DHCP** (modem local) |
| LAN | `bridge-lan` — `192.168.50.0/24`, gateway `.1` |
| ESP M1 / M2 / M3 | `.121` / `.145` / `.146` |
| WireGuard | `wg-sede`, listen **51821**, IP `10.255.0.50/32` |
| Endpoint produção | `177.74.79.32:51820` |

### 4.1 WAN + LAN

```
/ip dhcp-client add interface=ether1 disabled=no use-peer-dns=yes comment="WAN"
/interface bridge add name=bridge-lan
/interface bridge port add bridge=bridge-lan interface=ether2
/interface bridge port add bridge=bridge-lan interface=ether3
/interface bridge port add bridge=bridge-lan interface=ether4
/interface bridge port add bridge=bridge-lan interface=ether5
/ip address add address=192.168.50.1/24 interface=bridge-lan
/ip pool add name=pool-lan ranges=192.168.50.120-192.168.50.200
/ip dhcp-server add name=dhcp-lan interface=bridge-lan address-pool=pool-lan
/ip dhcp-server network add address=192.168.50.0/24 gateway=192.168.50.1 dns-server=8.8.8.8
/ip firewall nat add chain=srcnat out-interface=ether1 action=masquerade comment="NAT WAN"
/ip firewall filter add chain=forward action=accept connection-state=established,related,untracked place-before=0
/ip firewall filter add chain=forward action=accept in-interface=bridge-lan out-interface=ether1 place-before=0 comment="LAN para WAN"
```

### 4.2 WireGuard spoke (produção)

```
/interface wireguard add name=wg-sede listen-port=51821 mtu=1420
/ip address add address=10.255.0.50/32 interface=wg-sede
/interface wireguard peers add interface=wg-sede \
  public-key="pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU=" \
  endpoint-address=177.74.79.32 \
  endpoint-port=51820 \
  allowed-address=10.255.0.0/24,192.168.16.0/24 \
  persistent-keepalive=25s \
  comment="Hub RB ELEVA 1"
```

### 4.3 Firewall VPN (armário)

```
/ip firewall filter add chain=input in-interface=wg-sede action=accept place-before=0 comment="VPN input"
/ip firewall filter add chain=forward in-interface=wg-sede action=accept place-before=0 comment="VPN->LAN"
/ip firewall filter add chain=forward out-interface=wg-sede action=accept place-before=0 comment="LAN->VPN"
```

**PC fixo na LAN (ether4):** IP `192.168.50.10`, gateway `192.168.50.1`, DNS `8.8.8.8`.

---

## 5. PC Flask (192.168.16.130)

O servidor fica na **mesma LAN** da matriz — **não precisa** estar atrás do MikroTik.

### 5.1 Rota para LAN dos armários

No CMD **Administrador** (usar **IF** do adaptador `192.168.16.130`):

```
route delete 192.168.50.0
route add 192.168.50.0 mask 255.255.255.0 192.168.16.100 IF <numero> -p
route add 10.255.0.0 mask 255.255.0.0 192.168.16.100 IF <numero> -p
```

Ver interface: `route print` (lista no topo).

### 5.2 Firewall Windows

```
netsh advfirewall firewall add rule name="ELEVA Flask 15000" dir=in action=allow protocol=TCP localport=15000
```

Flask deve escutar em `0.0.0.0:15000` (`netstat -an | findstr 15000`).

---

## 6. Teste bancada — só 2 MikroTiks (validado ✅)

Sem internet/port forward — cabo entre matriz `ether2` e armário `ether1`.

| Equipamento | IP teste |
|-------------|----------|
| Matriz ether2 | `192.168.99.1/24` |
| Armário ether1 | `192.168.99.2/24` |
| Endpoint WG armário | `192.168.99.1:51820` (não usar IP público) |

**Testes OK:**

```
Armário: /ping 10.255.0.1
Matriz:  /ping 10.255.0.50
Matriz:  /ping 192.168.50.1
```

Após teste, voltar endpoint produção: `177.74.79.32:51820` e WAN armário em DHCP.

---

## 7. Teste produção (campo)

### Armário

```
/interface wireguard peers print detail
/ping 10.255.0.1 count=5
/ping 192.168.16.130 src-address=192.168.50.1 count=5
```

### Matriz

```
/interface wireguard peers print detail
/ping 10.255.0.50 count=5
/ping 192.168.50.1 count=5
```

### PC armário / Flask

```
http://192.168.16.130:15000
ping 192.168.16.130
```

Esperado: `last-handshake` recente, `rx/tx > 0`, ping OK.

---

## 8. Problemas comuns

| Sintoma | Causa | Solução |
|---------|-------|---------|
| `tx` sobe, `rx=0` | Port forward ou IP público errado | UDP 51820 → `.100`; IP `177.74.79.32` |
| Handshake ok, ping falha | Firewall `wg-sede` / `wg-eleva` | Regras input/forward (sec. 3.4 e 4.3) |
| Rotas 192.168.16.x **inativas** | Gateway `10.255.0.1` down | Reativar peer; usar `allowed-address` WG |
| Flask não abre | Rota PC na interface errada | `route add ... IF <adaptador 16.x>` |
| Ping `.130` ok só com `src=192.168.50.1` | Normal | ESPs usam `192.168.50.x` — OK |
| Chave errada no peer | Copiar hub no hub | Peer matriz = chave **armário** e vice-versa |

---

## 9. Arquivos e exports

```
D:\mikrotik\
  wg-keys.txt
  RB-ELEVA-1.rsc          ← export matriz
  RB-ELEVA-L050.rsc       ← export armário
  rede.txt

D:\
  ELEVA_LOCKER_Documentacao_RB_ARMARIO_RB_MATRIZ.docx
```

Comandos export:

```
/export file=RB-ELEVA-1
/export file=RB-ELEVA-L050
```

---

## 10. Referências no repositório

| Arquivo | Conteúdo |
|---------|----------|
| [MIKROTIK_VPN_HUB.md](MIKROTIK_VPN_HUB.md) | Matriz / hub sede |
| [MIKROTIK_ARMARIO_BANCADA.md](MIKROTIK_ARMARIO_BANCADA.md) | Armário bancada |
| [MIKROTIK_ARMARIO_PADRAO.md](MIKROTIK_ARMARIO_PADRAO.md) | Padrão por site |
| [tools/mikrotik_armario_padrao.rsc](../tools/mikrotik_armario_padrao.rsc) | Script ROS armário |
| [tools/mikrotik_rede_template.txt](../tools/mikrotik_rede_template.txt) | Planilha IPs/chaves |

---

## Checklist instalação campo

- [ ] Matriz na sede `192.168.16.100`
- [ ] Port forward UDP 51820 → `.100`
- [ ] Armário WAN modem local (DHCP)
- [ ] Endpoint `177.74.79.32:51820`
- [ ] ESPs `.121` `.145` `.146` no painel
- [ ] Rota Flask `192.168.50.0/24 → 192.168.16.100`
- [ ] Export `.rsc` em `D:\mikrotik\`
