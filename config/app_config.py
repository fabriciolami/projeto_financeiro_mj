# config/app_config.py
import os

APP_NAME = "SistemaPagamentos"
APP_VERSION = "1.0.1"

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
