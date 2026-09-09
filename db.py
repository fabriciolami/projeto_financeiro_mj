import os
import psycopg2
import logging
from config.supabase_client import get_supabase

def get_conn():
    try:
        return psycopg2.connect(
            host=os.environ["DB_HOST"],
            port=os.environ["DB_PORT"],
            dbname=os.environ["DB_NAME"],
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            sslmode="require"
        )
    except Exception:
        logging.critical("ERRO BANCO: falha ao conectar")
        raise


def buscar_configs():
    supabase = get_supabase()
    if supabase is None:
        raise RuntimeError("Supabase não configurado")

    response = (
        supabase
        .table("configs")
        .select("dia_salario, dia_adiantamento")
        .eq("id", 1)
        .single()
        .execute()
    )
    data = response.data
    return data["dia_salario"], data["dia_adiantamento"]


def salvar_configs(dia_salario, dia_adiantamento):
    supabase = get_supabase()
    if supabase is None:
        raise RuntimeError("Supabase não configurado")

    (
        supabase
        .table("configs")
        .update({
            "dia_salario": dia_salario,
            "dia_adiantamento": dia_adiantamento,
        })
        .eq("id", 1)
        .execute()
    )
