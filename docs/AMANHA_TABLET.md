# AMANHÃ — Tablet 7" no armário

> Checklist para deixar o ELEVA LOCKER pronto para demo/produção.

## Antes de dormir (PC servidor)

```cmd
cd C:\ElevaLocker
git pull
git checkout cursor/totem-seguro-c05c
tools\iniciar_tudo.bat
```

Confirme:
- [ ] http://192.168.16.130:15000 — painel OK
- [ ] /notificacoes — WhatsApp **conectado**
- [ ] ESP Matriz **online**

## Depósito no totem (v2.2)

Na tela inicial: **Depositar encomenda**

1. **PIN portaria** (teclado numérico) — `TOTEM_DEPOSITO_PIN=2026` no `.env`
2. **Escolher porta** — toque no compartimento livre (grade visual)
3. Destinatário + telefone → **Abrir porta selecionada**
4. Coloque a encomenda e **feche a porta**
5. Toque **Porta fechada — concluir** → WhatsApp enviado → **Depósito concluído!**

> **Sensor de porta (fase 2):** quando instalado no ESP32, o passo 5 será automático.

- **Código NÃO aparece** — só WhatsApp do morador após fechar a porta

## Configurar tablet (10" ou 7")

1. Conecte tablet na mesma WiFi
2. Abra Chrome → **http://192.168.16.130:15000/totem/3**
3. Menu ⋮ → **Adicionar à tela inicial** / Instalar app
4. **Sempre abrir no totem:** ver **`docs/TOTEM_TABLET_KIOSK.md`** (Fully Kiosk recomendado para fixar no armário)
5. Deixe tablet ligado na tomada — tela **nunca desligar**

Atalho PC: `tools\abrir_totem.bat` | Kiosk Windows: `tools\atalho_totem_kiosk.bat`

## Fluxo demo (5 min)

| # | Quem | Ação |
|---|------|------|
| 1 | Operador (celular) | Depositar encomenda + telefone |
| 2 | Morador | Recebe WhatsApp com código + link totem |
| 3 | Morador | Tablet → Retirar → 6 dígitos |
| 4 | Todos | Porta abre + compartimento **pisca na tela** |

**Operador NÃO vê código** — só morador no WhatsApp.

## Teste ESP offline (opcional)

Ver `docs/TESTE_ESP_OFFLINE.md`:
1. Depositar com servidor on
2. Ctrl+C no app.py
3. Retirar em http://192.168.16.162/
4. Religar com `iniciar_tudo.bat`

## Novidades desta versão

| Feature | Detalhe |
|---------|---------|
| Totem 3 telas | Início → código → sucesso |
| Mapa portas | Compartimento acende na tela |
| Rate limit | 8 tentativas / 5 min (anti brute-force) |
| Código expira | 7 dias (configurável) |
| WhatsApp premium | Link `/totem/3` + data validade |
| Ajuda totem | `TOTEM_AJUDA_TELEFONE` no .env |
| Som sucesso | Beep ao abrir porta |

## .env recomendado (adicione)

```env
ENCOMENDA_DIAS_VALIDADE=7
TOTEM_AJUDA_TELEFONE=(48) 99999-9999
```

## Comparado ao Meu Locker

| Item | Meu Locker | ELEVA |
|------|------------|-------|
| WhatsApp | ✅ | ✅ |
| Totem touch | ✅ | ✅ |
| Código oculto p/ depositante | ✅ | ✅ |
| Offline ESP | ✅ | ✅ |
| Portal próprio | Deles | **Seu** |
| White-label | Limitado | **Total** |

## Próximo sprint (pós-tablet)

- [ ] QR camera no totem
- [ ] Depósito self-service entregador
- [ ] Sensor porta aberta/fechada
- [ ] App morador PWA
