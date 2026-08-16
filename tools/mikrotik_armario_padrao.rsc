# ============================================================
# ELEVA LOCKER — MikroTik ARMÁRIO (spoke) — site 050 bancada
# Edite variáveis abaixo, cole no Terminal WinBox (RB armário)
# ============================================================

# --- VARIÁVEIS (alterar por site) ---
:local siteId "050"
:local siteNum 50
:local identity ("RB-ELEVA-L" . $siteId)
:local lanSubnet ("192.168." . $siteNum . ".0/24")
:local lanGateway ("192.168." . $siteNum . ".1")
:local vpnIp ("10.255.0." . $siteNum . "/32")
:local wifiSsid ("ELEVA - LOCKER " . $siteId)
:local wifiPass "eleva-locker-050"
:local wanIf "ether1"
:local hubPubKey "pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU="
:local hubEndpoint "COLOQUE_IP_PUBLICO_SEDE_AQUI"
:local hubPort 51820
:local flaskIp "192.168.16.130"

# --- Identity ---
/system identity set name=$identity

# --- WAN (internet local) ---
/ip dhcp-client remove [find]
/ip dhcp-client add interface=$wanIf disabled=no use-peer-dns=yes use-peer-ntp=yes comment="WAN cliente"

# --- Bridge LAN ---
/interface bridge add name=bridge-lan comment="LAN armario ESPs"
/interface bridge port add bridge=bridge-lan interface=ether2
/interface bridge port add bridge=bridge-lan interface=ether3
/interface bridge port add bridge=bridge-lan interface=ether4
/interface bridge port add bridge=bridge-lan interface=ether5

/ip address add address=($lanGateway . "/24") interface=bridge-lan comment="Gateway LAN"

# --- DHCP LAN ---
/ip pool add name=pool-lan ranges=("192.168." . $siteNum . ".120-192.168." . $siteNum . ".200")
/ip dhcp-server add name=dhcp-lan interface=bridge-lan address-pool=pool-lan disabled=no
/ip dhcp-server network add address=$lanSubnet gateway=$lanGateway dns-server=$lanGateway

# Reservas ESP (substituir MACs reais depois)
/ip dhcp-server lease add address=("192.168." . $siteNum . ".121") comment="ESP M1"
/ip dhcp-server lease add address=("192.168." . $siteNum . ".145") comment="ESP M2"
/ip dhcp-server lease add address=("192.168." . $siteNum . ".146") comment="ESP M3"

# --- WireGuard → hub sede ---
/interface wireguard add name=wg-sede listen-port=51821 mtu=1420 comment="VPN hub ELEVA"
/ip address add address=$vpnIp interface=wg-sede
/interface wireguard peers add interface=wg-sede public-key=$hubPubKey endpoint-address=$hubEndpoint endpoint-port=$hubPort allowed-address="10.255.0.0/24,192.168.16.0/24" persistent-keepalive=25s comment="Hub RB ELEVA 1"
/ip route add dst-address=($flaskIp . "/32") gateway=10.255.0.1 comment="Flask sede"

# --- Firewall mínimo ---
/ip firewall filter add chain=input protocol=udp dst-port=51821 action=accept comment="WG local"
/ip firewall filter add chain=forward action=accept comment="ELEVA VPN+LAN" place-before=0

# --- NAT WAN (ESP acessam internet para sync se precisar) ---
/ip firewall nat add chain=srcnat out-interface=$wanIf action=masquerade comment="NAT WAN"

# FIM — rodar: /interface wireguard print detail
# Copiar public-key → peer no hub + D:\mikrotik\wg-keys.txt
