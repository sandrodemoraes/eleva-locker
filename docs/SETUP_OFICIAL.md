# Setup oficial — ELEVA Locker Matriz

> Substitui o fluxo "Bancada Teste" para operação real no painel.

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
| Compartimentos | 8 portas (1–4 P, 5–6 M, 7 G, 8 GG) |

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
