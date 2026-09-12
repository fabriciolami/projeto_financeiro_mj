# styles.py
import tkinter as tk
from tkinter import font
import sys

BTN_VERDE = {
    "bg": "#2ecc71",
    "fg": "white",
    "relief": "flat",
    "bd": 0,
    "padx": 10,
    "pady": 5
}

BTN_AZUL = {
    "bg": "#3498db",
    "fg": "white",
    "relief": "flat",
    "bd": 0,
    "padx": 10,
    "pady": 5
}

BTN_ROXO = {
    "bg": "#9b59b6",
    "fg": "white",
    "relief": "flat",
    "bd": 0,
    "padx": 10,
    "pady": 5
}

BTN_PADRAO = {
    "bg": "#bdc3c7",
    "fg": "black",
    "relief": "flat",
    "bd": 0,
    "padx": 10,
    "pady": 5
}

BTN_VERMELHO = {    
    "bg": "#e74c3c",
    "fg": "white",
    "relief": "flat",
    "bd": 0,
    "padx": 10,
    "pady": 5
}


def add_hover(widget, bg_hover, fg_hover=None):
    bg_normal = widget.cget("bg")
    fg_normal = widget.cget("fg")
    relief_normal = widget.cget("relief")

    def on_enter(event):
        widget.config(bg=bg_hover, relief="raised")
        if fg_hover:
            widget.config(fg=fg_hover)

    def on_leave(event):
        widget.config(bg=bg_normal, fg=fg_normal, relief=relief_normal)

    widget.bind("<Enter>", on_enter)
    widget.bind("<Leave>", on_leave)

def centralizar_janela(janela, largura=None, altura=None):
    janela.update_idletasks()

    # Identifica o monitor antes de aumentar a janela. Assim, uma janela que
    # cresce sobre a segunda tela nao muda de monitor durante a centralizacao.
    largura = largura or janela.winfo_width()
    altura = altura or janela.winfo_height()

    # No Windows, winfo_screenwidth/height pode representar a area combinada
    # de varios monitores. Nesse caso, o centro calculado pode cair na segunda
    # tela. Usa a area util do monitor em que a janela ja se encontra.
    if sys.platform == "win32":
        try:
            import ctypes
            from ctypes import wintypes

            class MONITORINFO(ctypes.Structure):
                _fields_ = [
                    ("cbSize", wintypes.DWORD),
                    ("rcMonitor", wintypes.RECT),
                    ("rcWork", wintypes.RECT),
                    ("dwFlags", wintypes.DWORD),
                ]

            user32 = ctypes.windll.user32
            user32.MonitorFromWindow.argtypes = [wintypes.HWND, wintypes.DWORD]
            user32.MonitorFromWindow.restype = wintypes.HANDLE
            user32.GetMonitorInfoW.argtypes = [wintypes.HANDLE, ctypes.POINTER(MONITORINFO)]
            user32.GetMonitorInfoW.restype = wintypes.BOOL
            hwnd = janela.winfo_id()
            monitor = user32.MonitorFromWindow(hwnd, 2)  # monitor mais proximo
            info = MONITORINFO()
            info.cbSize = ctypes.sizeof(MONITORINFO)

            if monitor and user32.GetMonitorInfoW(monitor, ctypes.byref(info)):
                area = info.rcWork
                x = area.left + max(0, (area.right - area.left - largura) // 2)
                y = area.top + max(0, (area.bottom - area.top - altura) // 2)
                janela.geometry(f"{largura}x{altura}{x:+d}{y:+d}")
                return
        except (AttributeError, OSError):
            # Mantem compatibilidade com ambientes Windows sem essas APIs.
            pass

    tela_largura = janela.winfo_screenwidth()
    tela_altura = janela.winfo_screenheight()

    x = (tela_largura // 2) - (largura // 2)
    y = (tela_altura // 2) - (altura // 2)

    janela.geometry(f"{largura}x{altura}+{x}+{y}")

def preparar_janela(janela, largura, altura): # configura tamanho fixo
    janela.resizable(False, False) # desabilita redimensionamento
    centralizar_janela(janela, largura, altura) # dimensiona e centraliza
    janela.focus_force() # força foco na janela

def entry_rounded(master, show=None):
    container = tk.Frame(master, bg="#f2f4f8")

    canvas = tk.Canvas(container,
        width=280,
        height=38,
        bg="#f2f4f8",
        highlightthickness=0
    )
    canvas.pack()

    # desenha fundo
    bg_shape = canvas.create_rectangle(
        2, 2, 278, 36, 
        outline="#ccc", 
        width=2, 
        fill="white")

    entry = tk.Entry(
        container,bd=0,
        bg="white",
        font=("Segoe UI", 10),
        show=show)
    entry.place(x=14, y=10, width=235, height=18)

    # foco azul
    entry.bind("<FocusIn>", lambda e: canvas.itemconfig(bg_shape, outline="#1976d2"))
    entry.bind("<FocusOut>", lambda e: canvas.itemconfig(bg_shape, outline="#ccc"))
    
    return container, entry
