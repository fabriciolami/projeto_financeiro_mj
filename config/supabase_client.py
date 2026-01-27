# config/supabase_client.py
import logging

_supabase = None

def get_supabase():
    global _supabase

    if _supabase:
        return _supabase

    try:
        from supabase import create_client
        from config.app_config import SUPABASE_URL, SUPABASE_KEY

        _supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        return _supabase

    except Exception as e:
        logging.warning(f"Supabase offline: {e}")
        return None
