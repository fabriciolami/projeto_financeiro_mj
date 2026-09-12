import logging
import importlib.util
from pathlib import Path
from supabase import create_client

# Os arquivos locais são opcionais e não fazem parte do repositório.
# Aceita tanto o nome padrão quanto o nome legado usado no executável.
for config_name in ("local_config.py", "local.config.py"):
    config_path = Path(__file__).with_name(config_name)
    if not config_path.is_file():
        continue
    spec = importlib.util.spec_from_file_location("config.local_config", config_path)
    if spec is None or spec.loader is None:
        raise RuntimeError("Não foi possível carregar a configuração local do Supabase.")
    local_config = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(local_config)
    SUPABASE_URL = local_config.SUPABASE_URL
    SUPABASE_KEY = local_config.SUPABASE_KEY
    break
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
