
import sys
import logging as log
import os
import tkinter as tk
from tkinter import messagebox as mb

APP_INICIADO = False

# BASE DIR SEGURO (exe + dev)
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)
    
# IMPORTS DO SISTEMA
# =============================
from utils.updater import verificar_atualizacao, janela_progresso
from view.login_screen import LoginScreen
from view.main_app import App

# LOGGING ROBUSTO
# =============================
def setup_logging():
    log_base = (
        os.path.dirname(sys.executable)
        if getattr(sys, "frozen", False)
        else os.path.dirname(__file__)
    )

    log_dir = os.path.join(log_base, "logs")
    os.makedirs(log_dir, exist_ok=True)

    log_file = os.path.join(log_dir, "app.log")

    logger = log.getLogger()
    logger.setLevel(log.INFO)

    for h in logger.handlers[:]:
        logger.removeHandler(h)

    fh = log.FileHandler(log_file, encoding="utf-8")
    fh.setLevel(log.INFO)

    formatter = log.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s"
    )
    fh.setFormatter(formatter)

    logger.addHandler(fh)


        # =============================
        # SISTEMA PRINCIPAL
        # =============================
def iniciar_sistema():
    global APP_INICIADO

    # 🚫 BLOQUEIA LOOP DE INICIALIZAÇÃO
    if APP_INICIADO:
        return
    APP_INICIADO = True

    try:
        setup_logging()
        log.info("Sistema iniciando...")

        root = tk.Tk()
        root.withdraw()  # evita piscada e múltiplas janelas
        os.environ["ALLOW_UI_ALERTS"] = "1"

        if getattr(sys, "frozen", False):
            try:
                versao, url = verificar_atualizacao()
                if versao and url:
                    if mb.askyesno(
                        "Atualização disponível",
                        f"Nova versão {versao} disponível.\nDeseja atualizar agora?"
                    ):
                        janela_progresso(root, url)
                        root.mainloop()
                        return
            except Exception:
                log.exception("Falha no updater (ignorado)")
                # updater nunca pode matar o app

        root.deiconify()
        root.title("Sistema de Pagamentos")

        # =============================
        # CALLBACKS
        # =============================
        def abrir_main_app(usuario, perfil):
            try:
                for w in root.winfo_children():
                    w.destroy()
                App(root, usuario=usuario, perfil=perfil)
            except Exception:
                log.exception("Erro ao abrir App principal")

        def voltar_login(event=None):
            for w in root.winfo_children():
                w.destroy()
            LoginScreen(root, callback_sucesso=abrir_main_app)

        root.bind("<<Logout>>", voltar_login)

        LoginScreen(root, callback_sucesso=abrir_main_app)
        root.mainloop()

    except Exception:
        try:
            log.exception("ERRO NA INICIALIZAÇÃO")
        except Exception:
            pass
        os._exit(0)

if __name__ == "__main__":
    iniciar_sistema()
