import logging
from supabase import create_client

# tenta usar config local (fora do git)
try:
    from config.local_config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    from config.app_config import SUPABASE_URL, SUPABASE_KEY

_supabase = None


def get_supabase():
    global _supabase

    if _supabase is not None:
        return _supabase

    if not SUPABASE_URL or not SUPABASE_KEY:
        logging.error("Credenciais do Supabase não configuradas")
        return None

    try:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase
    except Exception:
        logging.exception("Supabase indisponível")
        return None
