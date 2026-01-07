from db import get_conn

try:
    conn = get_conn()
    print("✅ Conectado ao Supabase com sucesso!")
    conn.close()
except Exception as e:
    print("❌ Erro na conexão:", e)
