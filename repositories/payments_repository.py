from config.supabase_client import supabase

class PaymentsRepository:

    def listar_por_mes(self, mes, ano):
        response = (
            supabase
            .table("pagamentos")
            .select("*")
            .eq("mes", mes)
            .eq("ano", ano)
            .execute()
        )
        return response.data
