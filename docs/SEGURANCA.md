# Segurança — ELEVA LOCKER

Checklist prático após trocar a senha do admin.

## O que você já fez ✓

- **Senha forte do administrador** (sandro.demoraes@gmail.com)
- **PIN do Windows** no PC da bancada

## O que o sistema faz agora (código)

| Proteção | Descrição |
|----------|-----------|
| **Rate limit no login** | Máx. 10 tentativas / 15 min por IP — anti força bruta |
| **Sessão segura** | Cookie HttpOnly + SameSite (anti roubo de sessão) |
| **Senhas hash** | bcrypt/werkzeug — nunca salva senha em texto |
| **Totem retirada** | Máx. 8 tentativas de código / 5 min |
| **ESP32** | Token obrigatório — não expõe tamanho do token em erro |
| **Debug produção** | `FLASK_DEBUG=0` fora da bancada |

## Verificar sua bancada

```cmd
cd C:\ElevaLocker
tools\verificar_seguranca.bat
```

## Recomendado no `.env` (bancada)

```env
ELEVA_BANCADA=1
SECRET_KEY=<gere uma chave longa>
ESP32_TOKEN=2e5bb4db71d8330be8bae43b13ac19f6
TOTEM_DEPOSITO_SEM_PIN=1
TOTEM_DEPOSITO_SOMENTE_CADASTRADO=1
```

Gerar SECRET_KEY:
```cmd
python -c "import secrets; print(secrets.token_hex(32))"
```

## Totem na bancada

- **SEM PIN** (`TOTEM_DEPOSITO_SEM_PIN=1`) é aceitável se o tablet fica **físico no armário**, rede **192.168.x.x** only.
- Para condomínio com portaria: defina `TOTEM_DEPOSITO_PIN` com 6 dígitos **não óbvios** (não 2026, 1234).

## Produção (internet)

1. `FLASK_DEBUG=0`
2. `SECRET_KEY` e `ESP32_TOKEN` únicos
3. HTTPS (nginx/Caddy na frente)
4. Firewall — porta 15000 só na LAN ou VPN
5. Backup: `tools\backup_obrigatorio.bat`

## Próximas melhorias (futuro)

- CSRF nos formulários admin
- HTTPS integrado
- 2FA admin (opcional)

## Comandos úteis

| Comando | Função |
|---------|--------|
| `tools\verificar_seguranca.bat` | Checklist .env |
| `tools\limpar_admin_padrao.bat` | Remove admin@elevalocker.com |
| Configurações → Minha conta | Trocar sua senha |
