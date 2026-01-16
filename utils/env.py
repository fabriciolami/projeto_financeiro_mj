import os
import sys
from dotenv import load_dotenv

def carregar_env():
    if getattr(sys, "frozen", False):
        # Quando for .exe (PyInstaller)
        base_path = os.path.dirname(sys.executable)
    else:
        # Quando for python normal
        base_path = os.path.dirname(os.path.abspath(__file__))

    env_path = os.path.join(base_path, ".env")
    load_dotenv(env_path)
