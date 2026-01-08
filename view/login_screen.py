# view/login_screen.py
import tkinter as tk
from tkinter import messagebox
import db
db.get_conn() # Assumindo que seu arquivo db.py continua na raiz ou pasta database
from view.main_app import MainApp # Importaremos a classe principal daqui

class LoginScreen:
    def __init__(self, root):
        self.root = root
        root.title("Sistema Financeiro")
        root.geometry("350x300")

        tk.Label(root, text="Usuário").pack(pady=5)
        self.user = tk.Entry(root)
        self.user.pack()

        tk.Label(root, text="Senha").pack(pady=5)
        self.pwd = tk.Entry(root, show="*")
        self.pwd.pack()

        tk.Button(root, text="Entrar", command=self.login).pack(pady=20)

    def login(self):
        # DICA: Use 'with' para garantir fechamento da conexão
        conn = db.get_conn()
        try:
            with conn.cursor() as c:
                c.execute(
                    "SELECT perfil FROM usuarios WHERE login=%s AND senha=%s",
                    (self.user.get(), self.pwd.get())
                )
                r = c.fetchone()
        finally:
            conn.close()

        if r:
            self.root.destroy()
            # Inicia a nova janela principal
            root = tk.Tk()
            MainApp(root, r[0])
            root.mainloop()
        else:
            messagebox.showerror("Erro", "Login inválido")