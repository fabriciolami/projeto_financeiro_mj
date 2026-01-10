import psycopg2

def get_conn():
    return psycopg2.connect(
        host="aws-1-sa-east-1.pooler.supabase.com",
        database="postgres",
        user="postgres.jhgroptfwifgkfgatggz",
        password="REMOVED_USE_ENVIRONMENT_VARIABLE",
        port=6543,
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
