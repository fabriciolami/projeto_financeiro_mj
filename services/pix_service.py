# services/pix_service.py
from config import CIDADE_PIX, UF_PIX

def crc16(payload):
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            crc = ((crc << 1) ^ 0x1021) if crc & 0x8000 else crc << 1
            crc &= 0xFFFF
    return f"{crc:04X}"

def gerar_payload_pix(chave, valor, nome, txid):
    nome = nome[:25].upper()
    cidade = f"{CIDADE_PIX}/{UF_PIX}"
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