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
