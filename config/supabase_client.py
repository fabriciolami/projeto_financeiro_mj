# config/supabase_client.py

from supabase import create_client
from config.app_config import SUPABASE_URL, SUPABASE_KEY

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
