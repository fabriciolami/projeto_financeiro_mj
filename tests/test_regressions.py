import unittest
from decimal import Decimal
from unittest.mock import MagicMock, patch

from models import Funcionario, normalizar_data_admissao
from repositories.payments_repository import PaymentsRepository
from security.permissions import has_permission
from services.financial_service import FinancialService
from services.pix_service import crc16
from view.main_app import App


class RegressionTests(unittest.TestCase):
    def test_dates(self):
        self.assertEqual(normalizar_data_admissao("29/02/2024"), "2024-02-29")
        self.assertEqual(normalizar_data_admissao("2024-02-29"), "2024-02-29")
        with self.assertRaises(ValueError):
            normalizar_data_admissao("29/02/2025")

    def test_invalid_employee_never_writes(self):
        with patch("models.get_supabase") as client:
            for fields in ({"nome": " "}, {"nome": "Teste", "salario": -1},
                           {"nome": "Teste", "va": float("nan")},
                           {"nome": "Teste", "salario": float("inf")},
                           {"nome": "Teste", "salario": 10, "desconto": 11}):
                with self.subTest(fields=fields), self.assertRaises(ValueError):
                    Funcionario(**fields).salvar()
            client.assert_not_called()

    def test_money_totals(self):
        rows = [{"salario": "0.10", "va": "0.20", "desconto": "0", "adiantamento": "0.10"}] * 10
        totals = FinancialService.calcular_totais(rows)
        self.assertEqual(totals["total_salario_va"], Decimal("3.00"))
        self.assertEqual(totals["total_adiantamento"], Decimal("1.00"))

    def test_permissions(self):
        self.assertTrue(has_permission(" Master ", "marcar_pagamento"))
        self.assertFalse(has_permission("FINANCEIRO", "marcar_pagamento"))
        self.assertFalse(has_permission(None, "marcar_pagamento"))

    def test_crc_known_vector(self):
        self.assertEqual(crc16("123456789"), "29B1")

    def test_manual_payment_is_confirmed_and_duplicates_blocked(self):
        app = App.__new__(App)
        app.perfil, app.mes_atual, app.ano_atual = "MASTER", 9, 2026
        client = MagicMock()
        query = client.table.return_value
        query.select.return_value = query
        query.eq.return_value = query
        query.limit.return_value = query
        query.execute.return_value.data = []
        client.auth.get_user.return_value.user.id = "test-user"
        with patch("view.main_app.get_supabase", return_value=client):
            self.assertTrue(app._registrar_pagamento(1, "Adiantamento", 100))
            payload = query.insert.call_args.args[0]
            self.assertEqual(payload["status"], "CONFIRMADO")
            self.assertEqual(payload["confirmado_por"], "test-user")
            self.assertTrue(payload["confirmado_em"])
            query.insert.reset_mock()
            query.execute.return_value.data = [{"id": 1}]
            self.assertFalse(app._registrar_pagamento(1, "Adiantamento", 100))
            query.insert.assert_not_called()

    def test_payment_permission_checked_before_database(self):
        app = App.__new__(App)
        app.perfil = "FINANCEIRO"
        with patch("view.main_app.get_supabase") as client:
            with self.assertRaises(PermissionError):
                app._registrar_pagamento(1, "Adiantamento", 100)
            client.assert_not_called()

    def test_report_uses_confirmed_history(self):
        client = MagicMock()
        query = client.table.return_value
        for method in ("select", "eq", "order"):
            getattr(query, method).return_value = query
        query.execute.return_value.data = []
        with patch("repositories.payments_repository.get_supabase", return_value=client):
            self.assertEqual(PaymentsRepository().listar_por_mes(9, 2026), [])
        client.table.assert_called_once_with("historico_pagamentos")
        query.eq.assert_any_call("status", "CONFIRMADO")


if __name__ == "__main__":
    unittest.main()
