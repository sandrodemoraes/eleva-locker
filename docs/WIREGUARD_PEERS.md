# WireGuard — registro de peers por site

Planilha / pasta para cada condomínio conectado ao HUB Matriz.

**Uso:** gestão e suporte — **não** substitui servidor local (Modelo A).

---

## Tabela de peers (exemplo)

| Site | Código | LAN site | IP PC Flask | WG site | Público hub | Armário id | Status |
|------|--------|----------|-------------|---------|-------------|------------|--------|
| Matriz | matriz | 192.168.16.0/24 | 192.168.16.130 | — | — | 2 | ✅ Fase 1 |
| Piloto 050 | piloto-050 | 192.168.50.0/24 | 192.168.50.10 | 10.255.0.50/32 | 177.74.79.32:51820 | — | 🔄 Piloto |

Colunas obrigatórias por site novo:

| Coluna | Exemplo | Notas |
|--------|---------|-------|
| `codigo` | `piloto-050` | Igual `ELEVA_SITE_CODIGO` |
| `nome` | Condomínio Residencial X | Painel `/sites` |
| `lan_subnet` | `192.168.50.0/24` | Rede local ESP + PC |
| `pc_ip` | `192.168.50.10` | `APP_URL_BASE` — **local** |
| `wg_ip` | `10.255.0.50` | IP do peer no túnel |
| `wg_pubkey` | `abc123...` | Chave pública MikroTik/PC site |
| `hub_pubkey` | `def456...` | Chave pública RB Matriz |
| `allowed_address` | `10.255.0.50/32,192.168.50.0/24` | No peer do hub |
| `armario_id` | `3` | Totem + cadastro ESP |
| `api_key` | `elk_...` | `GET /api/v1/status` |

---

## Numeração sugerida

| Site # | Código | LAN | WG IP |
|--------|--------|-----|-------|
| Matriz | matriz | 192.168.16.0/24 | 10.255.0.1 (hub) |
| 050 | locker-050 | 192.168.50.0/24 | 10.255.0.50 |
| 051 | locker-051 | 192.168.51.0/24 | 10.255.0.51 |
| NN | locker-0NN | 192.168.NN.0/24 | 10.255.0.NN |

---

## Hub Matriz (RB ELEVA 1)

```
/interface wireguard add name=wg-eleva listen-port=51820 mtu=1420
/ip address add address=10.255.0.1/24 interface=wg-eleva
```

Peer site piloto 050:

```
/interface wireguard peers add interface=wg-eleva \
  public-key="<PUBKEY_SITE050>" \
  allowed-address=10.255.0.50/32,192.168.50.0/24 \
  comment="Locker-piloto-050"
/ip route add dst-address=192.168.50.0/24 gateway=10.255.0.50
```

Detalhes completos: [MIKROTIK_VPN_HUB.md](MIKROTIK_VPN_HUB.md)

---

## Teste de conectividade (Matriz → site)

Com túnel ativo:

```cmd
ping 10.255.0.50
curl -H "X-API-Key: elk_..." http://10.255.0.50:15000/api/v1/status
```

Navegador: `http://10.255.0.50:15000/dashboard` (suporte remoto)

---

## Pasta no disco D / Sites

```
Sites/piloto-050/
  rede.txt
  env.txt
  api_key.txt
  wireguard.txt    ← pubkeys, IPs WG, data ativação
  mikrotik.rsc     ← backup RouterOS (se B+)
```

---

## Offline + WireGuard

| Evento | Operação local (Modelo A) | Matriz via WG |
|--------|---------------------------|---------------|
| Internet cai | ✅ Site opera | ❌ Matriz não alcança |
| WG cai | ✅ Site opera | ❌ Matriz cega |
| Volta online | WhatsApp / filas | Sync manual ou API status |

---

*Ver também: [ARQUITETURA_REDE_FASES.md](ARQUITETURA_REDE_FASES.md), [INSTALACAO_SITE.md](INSTALACAO_SITE.md)*
