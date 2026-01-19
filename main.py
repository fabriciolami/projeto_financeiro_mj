# main.py
from utils.env import carregar_env
from utils.updater import verificar_atualizacao

import tkinter as tk
from tkinter import messagebox
import logging

from view.login_screen import LoginScreen
from view.main_app import App


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s"
    )


def iniciar_sistema():
    try:
        # 1️⃣ Ambiente e log
        carregar_env()
        setup_logging()

        # 2️⃣ Verifica atualização (popup)
        root = tk.Tk()
        root.withdraw()  # Esconde a janela principal temporariamente

        verificar_atualizacao(root)
        
        root.deiconify()  # Mostra a janela principal após a verificação

        # 3️⃣ Interface
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

    except Exception:
        logging.exception("Erro ao iniciar o sistema")
        messagebox.showerror(
            "Erro crítico",
            "Erro ao iniciar o sistema. Verifique os logs."
        )


if __name__ == "__main__":
    iniciar_sistema()
