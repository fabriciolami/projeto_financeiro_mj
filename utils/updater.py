import requests
import os
import sys
import subprocess
import threading
import time
from tkinter import Toplevel, Label, messagebox
from tkinter.ttk import Progressbar
from utils.version import APP_VERSION

GITHUB_API = "https://api.github.com/repos/fabriciolami/projeto_financeiro_mj/releases/latest"
GITHUB_TOKEN = "REMOVED_USE_ENVIRONMENT_VARIABLE"  # ⚠️ depois vamos mover para .env

HEADERS = {
    "Accept": "application/vnd.github+json",
    "Authorization": f"Bearer {GITHUB_TOKEN}"
}


def verificar_atualizacao():
    try:
        print("🔎 Verificando atualização...")
        headers = {
            "Authorization": f"Bearer {GITHUB_TOKEN}",
            "Accept": "application/vnd.github+json"
        }

        r = requests.get(GITHUB_API, headers=headers, timeout=5)
        print("STATUS:", r.status_code)

        if r.status_code != 200:
            print("ERRO API:", r.text)
            return None, None

        data = r.json()
        print("TAG:", data.get("tag_name"))
        print("ASSETS:", data.get("assets"))

        versao_online = data["tag_name"].lstrip("v")

        asset = next(
            (a for a in data["assets"] if a["name"].endswith(".exe")),
            None
        )

        if not asset:
            print("❌ Nenhum .exe encontrado no release")
            return None, None

        url_exe = asset["browser_download_url"]

        print("LOCAL:", APP_VERSION, "ONLINE:", versao_online)

        if versao_online > APP_VERSION:
            print("✅ Atualização disponível")
            return versao_online, url_exe

    except Exception as e:
        print("EXCEPTION:", e)

    print("⏭ Nenhuma atualização")
    return None, None



def janela_progresso(root, url):
    win = Toplevel(root)
    win.title("Atualizando sistema")
    win.geometry("400x130")
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

    r = requests.get(url, stream=True, headers=HEADERS)
    total = int(r.headers.get("Content-Length", 0))
    baixado = 0

    with open(novo_exe, "wb") as f:
        for chunk in r.iter_content(1024 * 1024):
            if chunk:
                f.write(chunk)
                baixado += len(chunk)
                barra["value"] = int((baixado / total) * 100)

    time.sleep(1)
    win.destroy()

    subprocess.Popen(
        f'cmd /c timeout 2 && move /Y "{novo_exe}" "{exe_atual}" && start "" "{exe_atual}"',
        shell=True
    )
    sys.exit()
