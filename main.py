# main.py
from utils.env import carregar_env
carregar_env()

import tkinter as tk
from tkinter import messagebox
import logging

from view.login_screen import LoginScreen
from view.main_app import App

def iniciar_sistema():
    def setup_logging():
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    def carregar_env():
        pass

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

    try:
        setup_logging()
        carregar_env()

        root = tk.Tk()
        root.withdraw()

        # 🔗 binding do logout
        root.bind("<<Logout>>", voltar_login)

        LoginScreen(root, callback_sucesso=abrir_main_app)

        root.deiconify()
        root.mainloop()
    except Exception as e:
        logging.exception("Erro ao iniciar o sistema")

if __name__ == "__main__":
    iniciar_sistema()
