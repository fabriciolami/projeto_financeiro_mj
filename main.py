# main.py
import sys
import os

# Garante que a raiz do projeto esteja no path (exe + python)
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

import tkinter as tk
from tkinter import messagebox
import logging

from utils.updater import verificar_atualizacao, janela_progresso
from view.login_screen import LoginScreen
from view.main_app import App


def setup_logging():
    if getattr(sys, 'frozen', False):
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    log_dir = os.path.join(base_path, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    logging.basicConfig(
        filename=log_file,
        level=logging.DEBUG,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def iniciar_sistema():
    try:
        # 1️⃣ Ambiente e log
        setup_logging()
        logging.info("Iniciando sistema...")

        # 2️⃣ Verifica atualização (popup)
        root = tk.Tk()
        # 3️⃣ Interface
        root.title("Sistema de Pagamentos")
        root.withdraw()  # Esconde a janela principal temporariamente

        # 🔔 updater NÃO bloqueia inicialização
        versao, url = verificar_atualizacao()
        if versao:
            if messagebox.askyesno(
                "Atualização disponível",
                f"Nova versão {versao} disponível.\nDeseja atualizar agora?"
            ):
                janela_progresso(root, url)
                return

        root.deiconify() # Mostra a janela principal

        def abrir_main_app(usuario, perfil):
            try:
                for widget in root.winfo_children():
                    widget.destroy()
                App(root, usuario=usuario, perfil=perfil)
            except Exception:
                logging.exception("Erro ao abrir Main App")
                messagebox.showerror(
                    "Erro",
                    "Erro ao abrir o sistema principal."
                )

        def voltar_login(event=None):
            for widget in root.winfo_children():
                widget.destroy()
            LoginScreen(root, callback_sucesso=abrir_main_app)

        # 🔗 binding do logout
        root.bind("<<Logout>>", voltar_login)

        LoginScreen(root, callback_sucesso=abrir_main_app)
        root.mainloop()

    except Exception:
        logging.exception("Erro ao iniciar o sistema")
        messagebox.showerror(
            "Erro crítico",
            "Erro ao iniciar o sistema. Verifique os logs."
        )


if __name__ == "__main__":
    iniciar_sistema()
