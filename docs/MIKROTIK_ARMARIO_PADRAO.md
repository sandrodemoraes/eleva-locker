# Padrão MikroTik — armário ELEVA LOCKER

Template repetível para cada armário (spoke WireGuard → hub sede).

## Nomenclatura por site

| Site | Identity | VPN IP | LAN | SSID Wi‑Fi |
|------|----------|--------|-----|------------|
| Bancada teste | `RB-ELEVA-L050` | `10.255.0.50/32` | `192.168.50.0/24` | `ELEVA - LOCKER 050` |
| Cliente 2 | `RB-ELEVA-L051` | `10.255.0.51/32` | `192.168.51.0/24` | `ELEVA - LOCKER 051` |
| Cliente N | `RB-ELEVA-L0NN` | `10.255.0.NN/32` | `192.168.NN.0/24` | `ELEVA - LOCKER 0NN` |

**ESPs (sempre iguais dentro de cada armário):** `.121` `.145` `.146`  
**Gateway LAN:** `.1`  
**Flask sede:** `http://192.168.16.130:15000`

## Portas físicas (padrão)

| Porta | Função |
|-------|--------|
| **ether1** | WAN — internet do local (cabo do condomínio) |
| **ether2–5** | LAN — bridge interna (ESPs, switch) |
| **Wi‑Fi** | Mesma bridge (ESPs + totem) |

> Se WAN for outra porta (ex. ether5), ajuste só o DHCP-client da WAN.

## Hub sede (fixo)

```
Public Key: pWWMpVG0lwuyqiKS0ja1zrpgsIa2Sud3nuJZygoIElU=
Endpoint:   IP_PUBLICO_SEDE:51820
```

## Aplicar padrão — bancada site 050

Ver script completo em `tools/mikrotik_armario_padrao.rsc` (variáveis no topo).

## Após configurar

1. `/interface wireguard print detail` → salvar Public Key armário
2. Adicionar peer no hub RB ELEVA 1
3. `/export file=armario-L050` → disco D
4. Gravar ESPs: WIFI_SSID + SERVIDOR_URL sede

Documentos: [MIKROTIK_VPN_HUB.md](MIKROTIK_VPN_HUB.md), [MIKROTIK_ARMARIO_BANCADA.md](MIKROTIK_ARMARIO_BANCADA.md)
