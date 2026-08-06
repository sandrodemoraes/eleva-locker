# Backup — ELEVA LOCKER no disco D:

> Protege banco de dados, `.env`, uploads e cópia do projeto inteiro.

## Estrutura no D:

```
D:\ElevaLockerBackup\
├── rotativo\          ← 5 backups automáticos (backup_01 … backup_05)
│   └── backup_01\
│       ├── database\elevalocker.db
│       ├── .env
│       └── ...
└── projeto\           ← espelho completo C:\ElevaLocker
    └── _ultimo_backup.txt
```

## Uso rápido

```cmd
cd C:\ElevaLocker
git pull
tools\backup_disco_d.bat
```

## Agendar todo dia (3h da manhã)

Clique direito → **Executar como administrador**:

```cmd
tools\instalar_backup_diario.bat
```

## Configurar no .env (opcional)

```env
BACKUP_DIR=D:\ElevaLockerBackup\rotativo
BACKUP_MAX=5
SKIP_BACKUP=0
```

- `SKIP_BACKUP=1` — desliga backup ao iniciar `app.py`
- Backup manual pelo painel: **Configurações → Criar backup**

## Restaurar

1. Pare `python app.py`
2. Painel → **Configurações → Restaurar backup #1**
3. Ou copie manualmente de `D:\ElevaLockerBackup\rotativo\backup_01\database\` para `C:\ElevaLocker\database\`

## Backup do Windows (sistema)

Além do ELEVA, recomendamos backup do Windows no D::

### Opção A — Histórico de Arquivos (mais simples)

1. Conecte/formate disco **D:**
2. **Configurações** → **Sistema** → **Armazenamento** → **Opções de backup avançadas**
   - Ou: **Configurações → Atualização e Segurança → Backup**
3. **Adicionar unidade** → escolha **D:**
4. Pastas importantes: `Documentos`, `Desktop`, `C:\ElevaLocker`

### Opção B — Imagem do sistema (recuperação completa)

1. **Painel de Controle** → **Backup e Restauração (Windows 7)**
2. **Criar imagem do sistema** → salvar em **D:**
3. Repetir mensalmente ou após mudanças grandes

### Opção C — Robocopy pasta ElevaLocker (extra)

Já incluído no `backup_disco_d.bat` (espelho em `D:\ElevaLockerBackup\projeto`).

## Checklist produção

| Item | Frequência |
|------|------------|
| `backup_disco_d.bat` | Diário (agendado) |
| Imagem Windows | Mensal |
| Testar restaurar backup #1 | Trimestral |
| Verificar D: com espaço livre | Semanal |

## Espaço estimado

| Conteúdo | Tamanho típico |
|----------|----------------|
| Banco SQLite | 1–50 MB |
| 5 rotativos | ~5× banco |
| Espelho projeto | ~20–100 MB |

Deixe **≥ 2 GB** livres no D:.
