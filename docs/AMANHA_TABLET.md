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

## Configurar tablet (manhã)

1. Conecte tablet na mesma WiFi
2. Abra Chrome → **http://192.168.16.130:15000/totem/3**
3. **F11** ou modo kiosk (tela cheia)
4. Opcional: Menu ⋮ → **Instalar app** / Adicionar à tela inicial
5. Deixe tablet ligado na tomada

Atalho no PC: `tools\abrir_totem.bat`

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
