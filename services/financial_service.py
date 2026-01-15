class FinancialService:

    @staticmethod
    def calcular_totais(registros):
        """
        registros: lista de dicts ou tuplas
        """
        total_salario_va = 0.0
        total_adiantamento = 0.0

        for r in registros:
            salario = float(r["salario"])
            va = float(r["va"])
            adiantamento = float(r["adiantamento"])

            total_salario_va += salario + va
            total_adiantamento += adiantamento

        return {
            "total_salario_va": total_salario_va,
            "total_adiantamento": total_adiantamento
        }
