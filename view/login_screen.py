# view/login_screen.py
import os
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
from PIL import ImageTk, Image
import db
from view.main_app import App # Importaremos a classe principal daqui
from styles import centralizar_janela
from styles import preparar_janela

class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Pagamento")
        self.root.geometry("400x500")
        centralizar_janela(self.root)
        preparar_janela(self.root, 400, 500)

        if os.path.exists("img/logo_empresa.png"):
            img = Image.open("img/logo_empresa.png").resize((350, 180))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(root, image=self.logo).pack(pady=20)

        tk.Label(root, text="Usuário").pack()
        self.ent_user = tk.Entry(root, width=25)
        self.ent_user.pack(pady=5)

        tk.Label(root, text="Senha").pack()
        self.ent_pass = tk.Entry(root, show="*", width=25)
        self.ent_pass.pack(pady=5)

        ttk.Button(root, text="Entrar", command=self.autenticar).pack(pady=30)

    def autenticar(self):
        conn = db.get_conn()
        c = conn.cursor()
        c.execute(
            "SELECT perfil FROM usuarios WHERE login=%s AND senha=%s",
            (self.ent_user.get(), self.ent_pass.get())
        )
        res = c.fetchone()
        conn.close()

        if res:
            self.root.destroy()
            root = tk.Tk()
            App(root, res[0])
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Login ou senha incorretos")