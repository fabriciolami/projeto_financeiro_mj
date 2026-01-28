from tkinter import messagebox
import os
import sys

def can_show_ui():
    """
    Só permite popup se:
    - não estiver rodando como serviço
    - não estiver em inicialização
    """
    return os.environ.get("ALLOW_UI_ALERTS") == "1"


def alert(tipo, msg, titulo=None):
    if not can_show_ui():
        # NÃO mostra popup
        return

    titulos = {
        "erro": "Erro",
        "aviso": "Atenção",
        "info": "Informação"
    }

    titulo_final = titulo or titulos.get(tipo, "Mensagem")

    if tipo == "erro":
        messagebox.showerror(titulo_final, msg)
    elif tipo == "aviso":
        messagebox.showwarning(titulo_final, msg)
    else:
        messagebox.showinfo(titulo_final, msg)


def confirm(title, message):
    if not can_show_ui():
        return False
    return messagebox.askyesno(title, message)
