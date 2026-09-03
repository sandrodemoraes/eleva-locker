# ELEVA LOCKER

Sistema inteligente de armários (lockers) para recebimento/retirada de encomendas.
Flask + SQLite (dev) / PostgreSQL (produção). UI em português. Porta padrão: `15000`.

Documentação de produto: `README.md`, `PROJETO.md` e `docs/`.

## Cursor Cloud specific instructions

Single Flask service (`app.py`). Dependencies live in a Python venv at `.venv` (created by the
startup update script). Activate it before running anything: `. .venv/bin/activate`.

### Run the app (dev)
- `. .venv/bin/activate && python app.py` — serves on `http://0.0.0.0:15000`.
- Runs with `debug=False` and no auto-reloader (see `app.py`), so **restart the process after
  code changes** — there is no hot reload.
- `python app.py` runs a blocking loop that intercepts Ctrl+C with a S/N prompt. In a
  non-interactive shell, start it under tmux and stop it by killing the specific PID.
- No `.env` is required: `config.py` defaults to SQLite and sensible values. `.env` is
  git-ignored; copy `.env.example` if you want to override (e.g. `SKIP_BACKUP=1`,
  `ESP32_MODO_SIMULACAO=1`). Postgres is only for production via `docker-compose.yml`.

### Database
- Dev uses SQLite at `database/elevalocker.db`, created automatically on startup by
  `criar_banco()`. The file is git-ignored; deleting it just recreates a fresh schema.
- A fresh DB seeds: admin user `admin@elevalocker.com` / `123456`, one site "Matriz",
  and default plans. It seeds **no armários** — several flows (totem, cadastro de morador)
  assume an armário exists; use `tools/recriar_matriz_armario.py` or the Armários UI to create one.

### Lint / tests
- No linter or test framework is configured. For a syntax sanity check use
  `python -m compileall app.py config.py database.py routes services repositories db`.
- Test helpers live in `tools/testar_*.py` / `tools/test_fase5.py`. Run e.g.
  `SKIP_BACKUP=1 python tools/test_fase5.py`. Some scripts start their own `app.test_client()`.
- Gotcha: `tools/test_fase5.py` "Totem" and `tools/testar_cadastro_armario.py` assume an
  armário with id `2` exists and that `TOTEM_ARMARIO_ID` is unset. On a clean DB with
  `TOTEM_ARMARIO_ID=2`, `/totem` returns a 302 redirect (not 200). Run test_fase5 with
  `TOTEM_ARMARIO_ID=` (empty) for a clean 17/17 pass. These are data/config expectations,
  not bugs.

### Notes
- ESP32 hardware calls are stubbed with `ESP32_MODO_SIMULACAO=1`; keep it on in the cloud VM.
- `SKIP_BACKUP=1` avoids the startup backup zip step.
