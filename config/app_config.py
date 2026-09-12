# config/app_config.py
import os

APP_NAME = "SistemaPagamentos"
from utils.version import APP_VERSION

CIDADE_PIX = "CRUZEIRO"
UF_PIX = "SP"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "",
    "database": "sistema_pagamentos",
    "port": 3306
}

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
