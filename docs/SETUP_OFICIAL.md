# Setup oficial — ELEVA Locker Matriz

> Substitui o fluxo "Bancada Teste" para operação real no painel.

## Fluxo simples (tudo no armário)

1. **Armários** → Novo armário → escolha **8 a 64 portas**
2. Clique no armário → **Gerenciar**
3. Dentro do armário:
   - **Adicionar ESP** (placa + IP → token para firmware)
   - **Compartimentos** criados automaticamente
   - **Usuários** cadastrados só neste armário

Não precisa mais ir em menus separados de ESP32 ou Compartimentos.

## Um comando

```cmd
cd C:\ElevaLocker
git pull
py tools/setup_oficial.py --ip-esp 192.168.16.162
```

Cria automaticamente:

| Item | Nome |
|------|------|
| Empresa | ELEVA Energia Solar |
| Armário | ELEVA Locker Matriz |
| ESP32 | ESP Matriz 8ch |
| Compartimentos | 8 portas padrão (configurável: **8, 16, 24, 32, 64**) |

```cmd
py tools/setup_oficial.py --ip-esp 192.168.16.162 --portas 8
```

## Alternar quantidade de portas

**No painel:** ESP32 → Editar → **Quantidade de portas** → Salvar  
(cria/atualiza compartimentos 1..N automaticamente)

**Via script:**

```cmd
py tools/ajustar_portas.py --portas 16
py tools/ajustar_portas.py --nome-esp "ESP Matriz 8ch" --portas 32
```

Opções: **8, 16, 24, 32, 64**

> **Hardware:** 8 relés = 1 placa BESTER. Para 16+ portas serão necessárias placas/expansores adicionais; o GPIO é atribuído em ciclo até o cadastro real por compartimento.

## Depois do script

1. Copie o **TOKEN** para `firmware/elevalocker_sync/elevalocker_sync.ino`
2. Confira `WIFI_PASSWORD` e `SERVIDOR_URL`
3. **Upload** no Arduino
4. Suba o servidor:

```cmd
set ESP32_MODO_SIMULACAO=0
set APP_URL_BASE=http://192.168.16.130:15000
py app.py
```

## Testar fluxo oficial

1. **Armários** → ELEVA Locker Matriz
2. **ESP32** → ESP Matriz 8ch (deve ficar 🟢 online)
3. **Compartimentos** → 8 portas com tamanhos
4. **Encomendas** → depositar pacote → código 6 dígitos
5. **Totem ESP** → http://192.168.16.162/ → retirar por código
6. **Teste relés** → http://192.168.16.130:15000/esp32/bancada

## GPIO (placa BESTER 8ch)

```
IN1→16  IN2→17  IN3→18  IN4→19
IN5→21  IN6→22  IN7→23  IN8→27
```

## Diagnóstico

```cmd
py tools/diagnostico_bancada.py --token SEU_TOKEN
```
