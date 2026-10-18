"""Mascaramento de telefone na UI (LGPD Fase 4)."""

import re

import config

ANONIMIZADO = "*** ANONIMIZADO ***"


class LgpdMascaraService:

    @staticmethod
    def deve_mascarar(perfil):
        if not config.LGPD_MASCARAR_TELEFONE:
            return False
        return perfil != "Administrador"

    @staticmethod
    def mascarar_telefone(telefone):
        if not telefone or telefone.strip() == ANONIMIZADO:
            return telefone or "—"

        digits = re.sub(r"\D", "", telefone)
        if len(digits) == 11:
            return f"({digits[:2]}) {digits[2:4]}**-**{digits[-2:]}"
        if len(digits) == 10:
            return f"({digits[:2]}) {digits[2:4]}**-**{digits[-2:]}"
        if len(digits) >= 4:
            return f"{'*' * max(0, len(digits) - 4)}{digits[-4:]}"
        return "****"

    @staticmethod
    def telefone_para_exibicao(telefone, perfil):
        if not LgpdMascaraService.deve_mascarar(perfil):
            return telefone or "—"
        return LgpdMascaraService.mascarar_telefone(telefone)

    @staticmethod
    def texto_para_exibicao(texto, perfil):
        """Mascara destinatário quando parece telefone."""
        if not texto or not LgpdMascaraService.deve_mascarar(perfil):
            return texto or "—"
        digits = re.sub(r"\D", "", texto)
        if len(digits) >= 8:
            return LgpdMascaraService.mascarar_telefone(texto)
        return texto
