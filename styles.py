# styles.py
import tkinter as tk

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
