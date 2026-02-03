import os
import psycopg2
import logging

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
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        SELECT dia_salario, dia_adiantamento
        FROM configs
        WHERE id = 1
    """)
    row = cur.fetchone()
    cur.close()
    conn.close()
    return row


def salvar_configs(dia_salario, dia_adiantamento):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        UPDATE configs
        SET dia_salario = %s,
            dia_adiantamento = %s
        WHERE id = 1
    """, (dia_salario, dia_adiantamento))
    conn.commit()
    cur.close()
    conn.close()
