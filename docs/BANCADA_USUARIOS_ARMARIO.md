# Bancada e produção — regras que evitam perda de dados

## Usuários do armário

Usuários ficam ligados ao armário pela coluna `usuarios.armario_id`.

**Nunca** devem sumir da página **Armários → abrir armário → Usuários** por causa de script de manutenção.

### O que causava o problema

1. `atualizar_visual_verde.bat` rodava `consertar_bancada` automaticamente
2. `consertar_bancada` excluía o armário **Bancada Teste**
3. O código antigo fazia `armario_id = NULL` nos usuários vinculados

### Proteções atuais (código)

| Camada | Comportamento |
|--------|----------------|
| `ArmarioService.excluir` | Migra usuários para **ELEVA Locker Matriz** (ou outro armário). **Bloqueia** exclusão se não houver destino. Não desvincula silenciosamente. |
| `limpar_bancada_teste.py` | Migra usuários para Matriz antes de excluir Bancada Teste |
| `consertar_bancada.py` | Backup `backups/vinculos_usuarios_latest.json` antes de limpar teste + `restaurar_usuarios_armario.py` |
| `atualizar_visual_verde.py` | **Só git pull** por padrão — **não** roda consertar (use `--com-consertar` se necessário) |

### Scripts — quando usar

| Script | Quando |
|--------|--------|
| `tools\iniciar_elevalocker.bat` | Uso diário — subir servidor |
| `tools\atualizar_visual_verde.bat` | Atualizar telas/código **sem** mexer em armário/usuários |
| `tools\consertar_bancada.bat` | ESP offline, token errado, 0 armários, totem quebrado |
| `tools\restaurar_usuarios_armario.bat` | Usuários sumiram do armário (recuperação) |
| `tools\diagnostico_usuarios_armario.bat` | Ver vínculos no banco sem alterar |

### Operador global vs operador do armário

- **Operador global** (`armario_id` vazio): vê todos os armários — aparece só em **Usuários**, não na página do armário. **Normal.**
- **Operador/síndico do condomínio**: cadastrar em **Armários → Matriz → Usuários** ou em Usuários com armário selecionado.

### Backup

Antes de `consertar_bancada`, o sistema grava:

- `backups/vinculos_usuarios_latest.json` — snapshot e-mail + armario_id
- `backups/backup_01/` — backup completo (quando `backup_obrigatorio` roda)

### Produção (depois da bancada)

1. Não rodar `consertar_bancada` em rotina — só emergência
2. Preferir `git pull` + reiniciar servidor
3. Backup diário (`tools\backup_obrigatorio.bat`) antes de atualizações
4. Nunca apagar armário com usuários sem confirmar migração (painel bloqueia se for o único armário)
