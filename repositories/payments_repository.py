from config.supabase_client import get_supabase


class PaymentsRepository:

    def listar_por_mes(self, mes, ano):
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase indisponivel no momento")
        
        response = (
            supabase
            .table("historico_pagamentos")
            .select("funcionario_id, tipo, valor, mes, ano, funcionarios(nome)")
            .eq("mes", mes)
            .eq("ano", ano)
            .eq("status", "CONFIRMADO")
            .order("funcionario_id")
            .execute()
        )
        return response.data

    def excluir(self, funcionario_id, tipos, mes, ano):
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase indisponível no momento")
        return (supabase.table("historico_pagamentos").delete()
                .eq("funcionario_id", funcionario_id).in_("tipo", tipos)
                .eq("mes", mes).eq("ano", ano).execute()).data
