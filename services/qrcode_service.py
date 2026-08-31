import io

import qrcode


class QrcodeService:

    @staticmethod
    def _gerar_png_bytes(conteudo):
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=10,
            border=4,
        )
        qr.add_data(conteudo)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#134736", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    @staticmethod
    def gerar_png_url(url):
        """Gera QR PNG com URL (ex.: página de cadastro)."""
        return QrcodeService._gerar_png_bytes((url or "").strip())

    @staticmethod
    def gerar_png(codigo, armario=None):

        conteudo = f"ELEVA:{codigo}"

        if armario:
            conteudo = f"ELEVA:{codigo}|{armario}"

        return QrcodeService._gerar_png_bytes(conteudo)

    @staticmethod
    def parse_conteudo(texto):

        texto = (texto or "").strip()

        if texto.startswith("ELEVA:"):

            partes = texto[6:].split("|")
            return {"codigo": partes[0], "armario": partes[1] if len(partes) > 1 else None}

        if texto.isdigit() and len(texto) == 6:
            return {"codigo": texto, "armario": None}

        return None
