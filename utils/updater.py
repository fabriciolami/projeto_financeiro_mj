import requests
import os
import sys
import subprocess
import threading
import time
import logging as log
from tkinter import Toplevel, Label, messagebox
from tkinter.ttk import Progressbar
from utils.version import APP_VERSION
from styles import centralizar_janela

GITHUB_API = "https://api.github.com/repos/fabriciolami/projeto_financeiro_mj_dist/releases/latest"


def verificar_atualizacao():
    try:
        print("🔎 Verificando atualização...")

        r = requests.get(GITHUB_API, timeout=8)
        print("STATUS:", r.status_code)

        if r.status_code != 200:
            print("ERRO API:", r.text)
            log.error("Updater: API status %s - %s", r.status_code, r.text)
            return None, None

        data = r.json()

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
        log.exception("Updater: falha ao verificar atualizacao")

    print("⏭ Nenhuma atualização")
    return None, None



def janela_progresso(root, url):
    win = Toplevel(root)
    win.title("Atualizando sistema")
    win.geometry("400x130")
    win.resizable(False, False)
    win.grab_set()
    centralizar_janela(win)

    Label(win, text="Baixando atualização...").pack(pady=10)

    barra = Progressbar(win, length=350, mode="determinate")
    barra.pack(pady=10)

    threading.Thread(
        target=baixar_e_atualizar,
        args=(url, barra, win),
        daemon=True
    ).start()


def baixar_e_atualizar(url, barra, win):
    base_dir = os.getenv("LOCALAPPDATA") or os.path.expanduser("~")
    pasta = os.path.join(base_dir, "SistemaPagamentos")
    os.makedirs(pasta, exist_ok=True)
    stamp = time.strftime("%Y%m%d_%H%M%S")
    novo_exe = os.path.join(pasta, f"SistemaPagamentos_update_{stamp}.exe")

    try:
        r = requests.get(url, stream=True, timeout=(8, 30))
        r.raise_for_status()
        total = int(r.headers.get("Content-Length", 0)) or 1
        baixado = 0
        last_log_at = time.time()
        last_log_bytes = 0

        with open(novo_exe, "wb") as f:
            for chunk in r.iter_content(1024 * 1024):
                if not chunk:
                    continue
                f.write(chunk)
                baixado += len(chunk)
                now = time.time()
                if now - last_log_at >= 5:
                    delta = baixado - last_log_bytes
                    log.info(
                        "Updater: baixado %.2f MB de %.2f MB (+%.2f MB em 5s)",
                        baixado / (1024 * 1024),
                        total / (1024 * 1024),
                        delta / (1024 * 1024)
                    )
                    last_log_at = now
                    last_log_bytes = baixado
                win.after(
                    0,
                    barra.configure,
                    {"value": int((baixado / total) * 100)}
                )

        win.destroy()

        # abre o novo exe
        subprocess.Popen([novo_exe], cwd=pasta)

        # fecha o atual
        os._exit(0)
    except Exception:
        log.exception("Updater: falha no download/execucao")
        try:
            win.destroy()
        except Exception:
            pass
        try:
            messagebox.showerror(
                "Atualizacao falhou",
                "Nao foi possivel baixar a atualizacao.\n"
                "Verifique sua conexao e permissoes e tente novamente."
            )
        except Exception:
            pass
