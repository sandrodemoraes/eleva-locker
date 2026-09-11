# WhatsApp (Evolution API) — operação e diagnóstico

O ELEVA LOCKER envia WhatsApp através da **Evolution API**, que roda em **Docker** no PC do site
(3 containers: `evolution-api`, `postgres`, `redis`). O envio é feito por
`services/notificacao_service.py` (provider `evolution`).

## Sintoma mais comum

Na tela do totem, ao concluir um depósito, aparece:

> Depósito concluído, mas WhatsApp não foi enviado. **Evolution API inacessível:
> `[WinError 10061] Nenhuma conexão pôde ser feita porque a máquina de destino as recusou ativamente`**

O `WinError 10061` = "conexão recusada" = **nada escutando na porta 8080**. Quase sempre significa
que os **containers da Evolution estão parados** (ex.: o PC reiniciou e eles não voltaram sozinhos).
Não é bug do sistema.

## Solução rápida (religar)

No **Docker Desktop → Terminal** (canto inferior direito) ou no **Prompt de Comando**:

```bat
REM 1) ver o estado dos containers
docker ps -a

REM 2) religar banco e cache primeiro
docker start elevalocker-evolution-postgres-1 elevalocker-evolution-redis-1

REM 3) esperar ~10s e religar a Evolution
docker start elevalocker-evolution-api-1

REM 4) conferir (os tres devem estar "Up" e a api com 0.0.0.0:8080->8080)
docker ps
```

Atalho: rode **`tools\iniciar_evolution.bat`** — ele faz os 3 passos, garante o reinício
automático e testa a porta 8080.

Depois, no navegador do PC, abra `http://localhost:8080` (tem que responder) e, no painel do ELEVA,
use **Reenviar** na encomenda pendente. O depósito já fica registrado; só a notificação é reenviada.

> Os nomes dos containers têm o prefixo do projeto Docker (aqui `elevalocker-evolution-*`).
> Se forem diferentes na sua máquina, confira com `docker ps -a` e ajuste.

## Para NÃO acontecer de novo

1. **Reinício automático dos containers** (uma vez só):
   ```bat
   docker update --restart unless-stopped elevalocker-evolution-postgres-1 elevalocker-evolution-redis-1 elevalocker-evolution-api-1
   ```
   Confirme: `docker inspect -f "{{.HostConfig.RestartPolicy.Name}}" elevalocker-evolution-api-1` → `unless-stopped`.
2. **Docker Desktop iniciar com o Windows**: Settings ⚙ → General → *Start Docker Desktop when you sign in*.
3. **Login automático do Windows** (`netplwiz`) no PC do totem, para que, após queda de energia,
   o PC ligue → logue → Docker suba → Evolution suba — sem intervenção.

## Checklist de verificação

- `docker ps` mostra os 3 containers `Up` e `evolution-api` com `0.0.0.0:8080->8080/tcp`.
- `http://localhost:8080` responde no navegador do PC.
- Instância `eleva-locker` conectada (QR escaneado). A sessão fica salva no volume
  `elevalocker_evolution_pg`, então normalmente **não** precisa reescanear após religar.
- No `.env`: `NOTIF_MODO=producao`, `NOTIF_WHATSAPP_ATIVO=1`, `WHATSAPP_API_URL=http://localhost:8080`,
  `WHATSAPP_INSTANCIA=eleva-locker`, `WHATSAPP_API_KEY=...`.

## Status pelo próprio sistema

O código expõe `NotificacaoService.status_whatsapp()`, usado na tela **Notificações** do painel,
que informa se está `ativo`, `configurado`, a conexão da instância e se está `pronto` para enviar.
