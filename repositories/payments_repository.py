from config.supabase_client import get_supabase


class PaymentsRepository:

    def listar_por_mes(self, mes, ano):
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase indisponivel no momento")
        
        response = (
            supabase
            .table("pagamentos")
            .select("*")
            .eq("mes", mes)
            .eq("ano", ano)
            .execute()
        )
        return response.data
