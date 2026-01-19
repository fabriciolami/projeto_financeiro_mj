import requests
import os
import sys
import subprocess
import json
import time

from version import APP_VERSION

UPDATE_URL = "https://servidor.com/version.json"

def verificar_atualizacao():
    try:
        r = requests.get(UPDATE_URL, timeout=5)
        data = r.json()

        versao_online = data["version"]
        url_exe = data["url"]

        if versao_online > APP_VERSION:
            return versao_online, url_exe

    except Exception as e:
        print("Erro ao verificar atualização:", e)

    return None, None


def baixar_e_atualizar(url):
    exe_atual = sys.executable
    pasta = os.path.dirname(exe_atual)
    novo_exe = os.path.join(pasta, "SistemaPagamentos_new.exe")

    r = requests.get(url, stream=True)
    with open(novo_exe, "wb") as f:
        for chunk in r.iter_content(1024):
            f.write(chunk)

    time.sleep(1)

    os.remove(exe_atual)
    os.rename(novo_exe, exe_atual)

    subprocess.Popen([exe_atual])
