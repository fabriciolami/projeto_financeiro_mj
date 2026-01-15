from decimal import Decimal, ROUND_HALF_UP

def format_money(valor: Decimal) -> str:
    if valor is None:
        valor = Decimal("0.00")

    valor = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return (
        f"R$ {valor:,.2f}"
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )