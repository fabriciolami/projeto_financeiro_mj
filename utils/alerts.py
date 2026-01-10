from tkinter import messagebox

def alert(tipo, msg, titulo=None):
    """
    tipo: 'erro' | 'aviso' | 'info'
    """
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

# SIM/NO confirmar dialogo
def confirm(title, message):
    return messagebox.askyesno(title, message)