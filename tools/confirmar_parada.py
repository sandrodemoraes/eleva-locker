"""Confirmacao de encerramento do servidor (Windows + Linux)."""

import sys


def perguntar_encerramento():
    print("\n\nEncerrar o servidor ELEVA LOCKER? (S/N): ", end="", flush=True)

    if sys.platform == "win32":
        import msvcrt

        while True:
            ch = msvcrt.getwch()
            print(ch)
            if ch in ("\r", "\n"):
                return True
            if ch.lower() in ("s", "y"):
                return True
            if ch.lower() == "n":
                return False

    try:
        resp = input().strip().lower()
    except (EOFError, KeyboardInterrupt):
        return True

    return resp in ("s", "sim", "y", "yes", "")


def instalar_handler_parada():
    import signal

    def handler(signum, frame):
        if perguntar_encerramento():
            print("\nServidor encerrado.")
            raise SystemExit(0)
        print("\nServidor continua.\n")

    signal.signal(signal.SIGINT, handler)
    if hasattr(signal, "SIGBREAK"):
        signal.signal(signal.SIGBREAK, handler)
