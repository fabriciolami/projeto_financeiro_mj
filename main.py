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
    import logging
    import os

    log_dir = os.path.join(os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__), "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    logger = logging.getLogger()
    logger.setLevel(logging.CRITICAL)

    # REMOVE handlers antigos (CRÍTICO!)
    for h in logger.handlers[:]:
        logger.removeHandler(h)

    fh = logging.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(logging.CRITICAL)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)


def iniciar_sistema():
    try:
        # 1️⃣ Ambiente e log
        setup_logging()
        logging.info("Iniciando sistema...")

        # 2️⃣ Tk Raiz
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal temporariamente

        # 🔔 updater NÃO bloqueia inicialização
        versao, url = verificar_atualizacao()
        if versao and url:
            if messagebox.askyesno(
                "Atualização disponível",
                f"Nova versão {versao} disponível.\nDeseja atualizar agora?"
            ):
                janela_progresso(root, url)
                root.mainloop()
                return

        root.deiconify() # Mostra a janela principal
        root.title("Sistema de Pagamentos")

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

    except Exception as e:
    logging.critical(f"ERRO FATAL: {e}", exc_info=True)
    messagebox.showerror(
        "Erro crítico",
        "O sistema encontrou um erro inesperado."
    )


if __name__ == "__main__":
    iniciar_sistema()
