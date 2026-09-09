import logging
import importlib.util
from pathlib import Path
from supabase import create_client

# Tenta usar a configuração local; em produção, usa variáveis de ambiente.
try:
    from config.local_config import SUPABASE_URL, SUPABASE_KEY
except ImportError:
    legacy_config = Path(__file__).with_name("local.config.py")
    if legacy_config.exists():
        spec = importlib.util.spec_from_file_location("config.local_config", legacy_config)
        local_config = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(local_config)
        SUPABASE_URL = local_config.SUPABASE_URL
        SUPABASE_KEY = local_config.SUPABASE_KEY
    else:
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
