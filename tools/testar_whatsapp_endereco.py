"""Verifica texto do WhatsApp de encomenda (sem IP local)."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SKIP_BACKUP", "1")
os.environ.setdefault("APP_URL_BASE", "http://192.168.16.130:15000")
os.environ.pop("NOTIF_INCLUIR_LINK_TOTEM", None)

from services.notificacao_service import NotificacaoService


def main():
    msg = NotificacaoService._montar_mensagem_whatsapp(
        cliente="sandra beatriz de moraes",
        armario="ELEVA Locker Matriz",
        compartimento=3,
        codigo="701507",
        armario_id=2,
        expira_em="2026-09-03 23:59:59",
    )
    print(msg)
    print()
    assert "192.168." not in msg, "IP local não deve aparecer no WhatsApp"
    assert "ELEVA Locker Matriz" in msg
    assert "701507" in msg
    assert "totem do armário" in msg.lower() or "totem" in msg.lower()
    print("OK — mensagem sem IP local")


if __name__ == "__main__":
    main()
