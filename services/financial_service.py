from decimal import Decimal


class FinancialService:

    @staticmethod
    def calcular_totais(registros):
        """
        registros: lista de dicionários com valores numéricos ou strings decimais.
        """
        total_salario_va = Decimal("0.00")
        total_adiantamento = Decimal("0.00")

        for r in registros:
            salario = Decimal(str(r["salario"] or 0))
            va = Decimal(str(r["va"] or 0))
            desconto = Decimal(str(r["desconto"] or 0))
            adiantamento = Decimal(str(r["adiantamento"] or 0))

            total_salario_va += salario + va - desconto
            total_adiantamento += adiantamento

        return {
            "total_salario_va": total_salario_va,
            "total_adiantamento": total_adiantamento
        }
