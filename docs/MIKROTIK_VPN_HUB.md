# MikroTik VPN — Upgrade ROS 7 + WireGuard (sede)

Guia para **RB ELEVA 1** (hEX, `192.168.16.100`) — hub VPN dos armários ELEVA LOCKER.

**Servidor Flask:** `192.168.16.130:15000` (PC na mesma LAN — porta **não** vai no MikroTik).

---

## Amanhã de manhã — ordem dos passos

### 1. Antes de atualizar (15 min)

- [ ] WinBox conectado em `192.168.16.100`
- [ ] **Backup:** `Files` → `Backup` → salvar `.backup` no disco D
- [ ] **Export:** Terminal → `/export file=eleva-pre-ros7`
- [ ] Anotar: quais portas WAN/LAN, DHCP, regras de firewall atuais
- [ ] Avisar se alguém depende da internet da sede (upgrade reinicia o roteador)
- [ ] PC servidor ligado — depois do upgrade testar `http://192.168.16.130:15000`

### 2. Atualizar RouterOS 6.49 → 7.x

- [ ] WinBox → notificação de update **ou** `System` → `Packages` → `Check For Updates`
- [ ] Instalar **RouterOS 7.x stable** (não apenas 6.49.20 — precisa da **v7** para WireGuard)
- [ ] Reinicia sozinho — reconectar WinBox
- [ ] Confirmar: `System` → `Resources` → versão **7.x**

> Se o channel stable não oferecer v7 no hEX, usar `System` → `Packages` → `Change Channel` → **stable** v7 ou download manual em mikrotik.com (arquitetura **mmips**).

### 3. WireGuard — hub na sede (RB ELEVA 1)

Valores de exemplo — site piloto **#50**:

| Papel | Endereço |
|-------|----------|
| Hub (sede) WG | `10.255.0.1/24` |
| Armário #50 WG | `10.255.0.50/32` |
| LAN armário (ESPs) | `192.168.50.0/24` |
| ESP M1/M2/M3 | `.121` / `.145` / `.146` |

**No RB ELEVA 1** (Terminal ou WinBox → WireGuard):

```
/interface wireguard add name=wg-eleva listen-port=51820 mtu=1420
/ip address add address=10.255.0.1/24 interface=wg-eleva
```

Gerar chave do hub (WinBox: WireGuard → + → copiar public key).

**Peer do armário #50** (substituir `<PUBKEY_ARMARIO50>`):

```
/interface wireguard peers add interface=wg-eleva \
  public-key="<PUBKEY_ARMARIO50>" \
  allowed-address=10.255.0.50/32,192.168.50.0/24 \
  comment="Locker-050"
```

**Rota** (tráfego para ESPs do site 50 via túnel):

```
/ip route add dst-address=192.168.50.0/24 gateway=10.255.0.50
```

### 4. Firewall sede (mínimo)

```
/ip firewall filter add chain=input protocol=udp dst-port=51820 \
  action=accept comment="WireGuard armarios"
/ip firewall filter add chain=forward src-address=192.168.50.0/24 \
  dst-address=192.168.16.130 action=accept comment="Armario50 -> Flask"
/ip firewall filter add chain=forward src-address=192.168.16.130 \
  dst-address=192.168.50.0/24 action=accept comment="Flask -> ESPs"
```

Ajustar ordem conforme suas regras existentes (accept antes de drop geral).

### 5. Internet → sede (roteador upstream)

Encaminhar **UDP 51820** → `192.168.16.100` (RB ELEVA 1).

**Não** encaminhar 15000 para o MikroTik.

### 6. WireGuard — MikroTik do armário (spoke)

No MikroTik **dentro do armário** (configurar na bancada antes de instalar):

```
/interface wireguard add name=wg-sede listen-port=51821
/ip address add address=10.255.0.50/32 interface=wg-sede
```

Peer apontando para IP público/DDNS da sede + pubkey do hub:

```
/interface wireguard peers add interface=wg-sede \
  public-key="<PUBKEY_HUB>" \
  endpoint-address=<IP_PUBLICO_OU_DDNS_SEDE> \
  endpoint-port=51820 \
  allowed-address=10.255.0.0/24,192.168.16.0/24 \
  persistent-keepalive=25s \
  comment="Hub ELEVA sede"
```

Rota para servidor:

```
/ip route add dst-address=192.168.16.130/32 gateway=10.255.0.1
```

Wi‑Fi LAN armário: `192.168.50.0/24`, DHCP estático ESPs `.121`, `.145`, `.146`.

### 7. Firmware ESP (armário piloto)

```cpp
const char* WIFI_SSID     = "ELEVA - LOCKER 050";
const char* SERVIDOR_URL  = "http://192.168.16.130:15000";
```

### 8. Testes (na ordem)

- [ ] WinBox: peer WireGuard **RX/TX** aumentando (sede ↔ armário)
- [ ] Do PC sede: ping `10.255.0.50` e ping `192.168.50.121`
- [ ] Painel: ESP **online**
- [ ] `py tools\validar_portas_bancada.py --amostra`
- [ ] Totem: `http://192.168.16.130:15000/totem/<id>`

### 9. Salvar no disco D

```
D:\ElevaLocker\Sites\Locker-050\
  mikrotik-hub.rsc      ← export sede
  mikrotik-armario.rsc  ← export armário
  rede.txt              ← IPs, SSID, DDNS, porta WG
  wg-keys.txt           ← chaves públicas (privadas só offline seguro)
```

---

## Referência rápida

| Porta | Onde | Para quê |
|-------|------|----------|
| **UDP 51820** | RB ELEVA 1 (WAN) | Armários conectam VPN |
| **TCP 15000** | PC `.130` | Flask — **só LAN/VPN**, não expor na web |
| **TCP 80** | ESPs `.121` etc. | Relé — só via VPN |

---

## Se algo der errado

- Restaurar backup: `System` → `Backup` → Upload `.backup`
- ROS 7 não instala: manter ROS 6 + **IPsec** temporário (pedir guia IPsec)
- ESP online mas relé não abre: rota/firewall `192.168.16.130` ↔ `192.168.50.0/24`

Documento relacionado: [INSTALACAO_SITE.md](INSTALACAO_SITE.md)
