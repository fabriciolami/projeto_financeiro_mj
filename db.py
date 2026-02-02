import psycopg2
import os
import logging

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT", 5432)),
        sslmode="require"
    )


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
