# services/pix_service.py
from config.app_config import CIDADE_PIX
import re

def crc16(payload):
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def normalizar_chave_pix(chave):
    if chave is None:
        return ""

    # remove espacos e caracteres invisiveis comuns
    chave = re.sub(r"[\s\u200b\u200c\u200d\ufeff]+", "", chave.strip())
    if not chave:
        return ""

    # email
    if "@" in chave:
        return chave.lower()

    # chave aleatoria (UUID/EVP)
    if re.fullmatch(r"[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}", chave):
        return chave.lower()

    # cpf/cnpj com prefixo textual (ex: "CPF = 123...")
    if re.search(r"\bcpf\b", chave, re.IGNORECASE) or re.search(r"\bcnpj\b", chave, re.IGNORECASE):
        digits = re.sub(r"\D", "", chave)
        if len(digits) in (11, 14):
            return digits

    # cpf/cnpj/telefone com pontuacao
    if re.fullmatch(r"[\d\.\-\/\(\)\+\s]+", chave):
        digits = re.sub(r"\D", "", chave)
        if chave.startswith("+"):
            return "+" + digits
        if len(digits) in (11, 14):
            return digits
        if len(digits) in (10, 11):
            return "+55" + digits
        if len(digits) in (12, 13) and digits.startswith("55"):
            return "+" + digits
        return digits

    # fallback: se tiver 11/14 digitos misturados com texto, assume CPF/CNPJ
    digits = re.sub(r"\D", "", chave)
    if digits and len(digits) in (11, 14):
        return digits

    return chave

def gerar_payload_pix(chave, valor, nome, txid):
    chave = normalizar_chave_pix(chave)
    if not chave:
        raise ValueError("Chave PIX vazia ou inválida.")
    if len(chave) > 77:
        raise ValueError("Chave PIX muito longa (máx. 77 caracteres).")
    nome = nome[:25].upper()
    cidade = CIDADE_PIX[:15].upper()  # 🔥 SEM UF, SEM BARRA
    valor_str = f"{valor:.2f}"

    def campo(id, valor):
        return f"{id}{len(valor):02}{valor}"

    payload = (
        campo("00", "01") +
        campo("26",
        campo("00", "BR.GOV.BCB.PIX") +
        campo("01", chave)
        ) +
        campo("52", "0000") +
        campo("53", "986") +
        campo("54", valor_str) +
        campo("58", "BR") +
        campo("59", nome) +
        campo("60", cidade) +
        campo("62",
            campo("05", txid)
        )
    )

    payload_com_crc = payload + "6304"
    return payload_com_crc + crc16(payload_com_crc)
