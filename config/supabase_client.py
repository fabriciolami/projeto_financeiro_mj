import logging
from supabase import create_client
from config.app_config import SUPABASE_URL, SUPABASE_KEY

_supabase = None

def get_supabase():
    global _supabase

    if _supabase is not None:
        return _supabase

    try:
        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase
    except Exception:
        logging.exception("Supabase indisponível")
        return None
