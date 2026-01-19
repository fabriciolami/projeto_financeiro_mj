import requests
import os
import sys
import subprocess
import threading
import time
from tkinter import Toplevel, Label
from tkinter.ttk import Progressbar
from tkinter import messagebox

try:
    from utils.version import APP_VERSION
except ImportError:
    from version import APP_VERSION


GITHUB_API = "https://api.github.com/repos/fabriciolami/projeto_financeiro_mj/releases/latest"


def verificar_atualizacao(root=None):
    try:
        r = requests.get(GITHUB_API, timeout=5)
        if r.status_code != 200:
            return

        data = r.json()
        versao_online = data["tag_name"].replace("v", "")

        if versao_online > APP_VERSION:
            if messagebox.askyesno(
                "Atualização disponível",
                f"Nova versão {versao_online} disponível.\n\nDeseja atualizar agora?"
            ):
                url = data["assets"][0]["browser_download_url"]
                janela_progresso(root, url)

    except Exception as e:
        print("Erro ao verificar atualização:", e)


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
