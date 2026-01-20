import requests
import os
import sys
import subprocess
import threading
import time
from tkinter import Toplevel, Label
from tkinter.ttk import Progressbar
from utils.version import APP_VERSION


GITHUB_API = "https://api.github.com/repos/fabriciolami/projeto_financeiro_mj/releases/latest"


def verificar_atualizacao():
    try:
        r = requests.get(GITHUB_API, timeout=5)

        if r.status_code != 200:
            return None, None

        data = r.json()

        versao_online = data["tag_name"].lstrip("v")

        asset = next(
            (a for a in data["assets"] if a["name"].endswith(".exe")),
            None
        )

        if not asset:
            return None, None

        url_exe = asset["browser_download_url"]

        if versao_online > APP_VERSION:
            return versao_online, url_exe

    except Exception:
        pass

    return None, None



def janela_progresso(root, url):
    win = Toplevel(root)
    win.title("Atualizando sistema")
    win.geometry("400x120")
    win.resizable(False, False)
    win.grab_set()

    Label(win, text="Baixando atualização...").pack(pady=10)

    barra = Progressbar(win, length=350, mode="determinate")
    barra.pack(pady=10)

    threading.Thread(
        target=baixar_e_atualizar,
        args=(url, barra, win),
        daemon=True
    ).start()


def baixar_e_atualizar(url, barra, win):
    exe_atual = sys.executable
    pasta = os.path.dirname(exe_atual)
    novo_exe = os.path.join(pasta, "SistemaPagamentos_update.exe")

    r = requests.get(url, stream=True)
    total = int(r.headers.get("Content-Length", 0))
    baixado = 0

    with open(novo_exe, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)
                baixado += len(chunk)
                progresso = int((baixado / total) * 100)
                barra["value"] = progresso

    time.sleep(1)
    win.destroy()

    subprocess.Popen(
        f'cmd /c timeout 2 && move /Y "{novo_exe}" "{exe_atual}" && start "" "{exe_atual}"',
        shell=True
    )
    sys.exit()
