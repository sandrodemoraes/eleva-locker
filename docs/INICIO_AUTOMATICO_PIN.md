# Início automático — PC com PIN do Windows

## Por que não entrou sozinho?

O ELEVA LOCKER hoje usa a pasta **Inicializar do Windows** (`Startup`). Esses programas só rodam **depois que alguém faz login** (digita PIN ou senha).

Se o PC reiniciou (Windows Update, queda de energia) e ficou na **tela de bloqueio pedindo PIN**, o usuário ainda **não entrou** → o servidor **não sobe**.

Isso é normal no Windows — não é bug do ELEVA LOCKER.

---

## Solução rápida (agora)

1. Digite o **PIN** e entre no Windows
2. Aguarde ~30 segundos **ou** rode manualmente:
   ```cmd
   C:\ElevaLocker\iniciar_elevalocker.bat
   ```
3. Abra `http://localhost:15000`

---

## Solução A — PC só da bancada (recomendado): login automático

Para o PC **ligar e abrir o ELEVA LOCKER sem PIN**, use **login automático com senha** (PIN sozinho não serve para isso).

### Passo a passo

1. **Criar senha na conta** (se só usa PIN hoje):
   - Configurações → Contas → Opções de entrada → **Senha** → Adicionar

2. **Ativar login automático:**
   - `Win + R` → digite `netplwiz` → Enter
   - **Desmarque** “Os usuários devem digitar nome e senha…”
   - OK → informe a **senha da conta** (não é o PIN de 4 dígitos)
   - Reinicie o PC para testar

3. **Reinstalar início automático do ELEVA:**
   ```cmd
   cd C:\ElevaLocker
   git pull origin cursor/ui-eleva-verde-c05c
   tools\instalar_inicio_automatico.bat
   ```

4. **Docker Desktop** (WhatsApp):
   - Docker → Settings → General → **Start Docker Desktop when you sign in**

Após reiniciar, o Windows entra sozinho → pasta Inicializar roda → ELEVA LOCKER sobe.

> **Segurança:** use login automático só em PC **fixo da bancada**, não em notebook pessoal.

---

## Solução B — Manter PIN + tarefa agendada (entra uma vez após reiniciar)

Se quiser **continuar com PIN**, não dá para subir o painel **antes** de alguém digitar o PIN.  
Mas dá para garantir que, **logo após o login**, o servidor inicia (com atraso para rede/Docker):

```cmd
cd C:\ElevaLocker
tools\instalar_inicio_automatico_tarefa.bat
```

Isso cria tarefa no **Agendador de Tarefas** (“ao fazer logon”, atraso 45 s).

Fluxo após reboot: **PIN uma vez** → tarefa roda sozinha → painel abre.

---

## Solução C — Acordar após queda de luz (BIOS)

Se o PC desligou de vez:

- Entre na **BIOS/UEFI** → **Power** → **After Power Loss** / **AC Power Recovery** → **Power On**
- Assim, quando voltar a energia, o PC liga sozinho (ainda precisa Solução A ou B para o ELEVA LOCKER)

---

## Conferir se está instalado

Pasta Inicializar deve ter:
```
%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\ELEVA LOCKER - Iniciar.lnk
```

Destino do atalho:
```
cmd /c C:\ElevaLocker\iniciar_elevalocker.bat
Iniciar em: C:\ElevaLocker
```

Agendador (Solução B): tarefa **ELEVA LOCKER - Iniciar**

---

## Resumo

| Cenário | O que fazer |
|---------|-------------|
| Reiniciou, pediu PIN | Digite PIN **ou** configure login automático (Solução A) |
| Quer zero PIN na bancada | `netplwiz` + senha + `instalar_inicio_automatico.bat` |
| Quer manter PIN | `instalar_inicio_automatico_tarefa.bat` (PIN 1× após cada reboot) |
| Queda de luz | BIOS “Power On” + Solução A |
