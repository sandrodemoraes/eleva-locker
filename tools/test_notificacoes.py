#!/usr/bin/env python3
"""Testes unitários — notificações (telefone BR, templates)."""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.notificacao_service import NotificacaoService


def test_telefone_celular():
    numero, erro = NotificacaoService.validar_telefone_br("11 99999-8888")
    assert erro is None, erro
    assert numero == "5511999998888"


def test_telefone_com_55():
    numero, erro = NotificacaoService.validar_telefone_br("+55 11 99999-8888")
    assert erro is None, erro
    assert numero == "5511999998888"


def test_telefone_fixo():
    numero, erro = NotificacaoService.validar_telefone_br("1133334444")
    assert erro is None, erro
    assert numero == "551133334444"


def test_telefone_invalido():
    _, erro = NotificacaoService.validar_telefone_br("123")
    assert erro is not None


def test_telefone_sem_nono():
    _, erro = NotificacaoService.validar_telefone_br("11588887777")
    assert erro is not None


def test_mensagem_whatsapp_tem_codigo():
    msg = NotificacaoService._montar_mensagem_whatsapp(
        "Maria", "Armário Matriz", 3, "123456"
    )
    assert "123456" in msg
    assert "Maria" in msg
    assert "totem" in msg.lower() or "/totem" in msg


def test_mensagem_email_sem_markdown():
    msg = NotificacaoService._montar_mensagem_email(
        "Maria", "Armário Matriz", 3, "123456"
    )
    assert "*" not in msg
    assert "123456" in msg


def test_formatar_resultado():
    texto = NotificacaoService.formatar_resultado_notificacoes([
        {"canal": "whatsapp", "sucesso": True},
        {"canal": "email", "sucesso": False, "mensagem": "SMTP offline"},
    ])
    assert "whatsapp: OK" in texto
    assert "email: SMTP offline" in texto


if __name__ == "__main__":
    testes = [
        test_telefone_celular,
        test_telefone_com_55,
        test_telefone_fixo,
        test_telefone_invalido,
        test_telefone_sem_nono,
        test_mensagem_whatsapp_tem_codigo,
        test_mensagem_email_sem_markdown,
        test_formatar_resultado,
    ]
    falhas = 0
    for t in testes:
        try:
            t()
            print(f"OK  {t.__name__}")
        except AssertionError as e:
            falhas += 1
            print(f"FAIL {t.__name__}: {e}")
    print(f"\n{falhas} falha(s) de {len(testes)}")
    sys.exit(1 if falhas else 0)
