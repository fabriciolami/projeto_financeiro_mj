# utils/env.py
import os
import sys
from dotenv import load_dotenv

def carregar_env():
    try:
        base_path = sys._MEIPASS  # PyInstaller
    except Exception:
        base_path = os.path.abspath(".")

    env_path = os.path.join(base_path, ".env")
    load_dotenv(env_path)

