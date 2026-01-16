# utils/paths.py
import os
import sys

def resource_path(relative_path):
    """
    Retorna o caminho correto tanto no Python normal
    quanto no .exe do PyInstaller (onefile ou onedir)
    """
    try:
        base_path = sys._MEIPASS  # PyInstaller (onefile)
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
