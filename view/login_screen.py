# view/login_screen.py
import os # para verificar se o arquivo de logo existe
import logging # para logar erros de banco
import tkinter as tk
from tkinter import messagebox # para mostrar mensagens de erro
from PIL import ImageTk, Image # para carregar a logo e os ícones de olho
import db # para conectar ao banco e autenticar o usuário
from styles import centralizar_janela
from styles import preparar_janela
from styles import entry_rounded
from utils.paths import resource_path
from utils.version import APP_VERSION

class LoginScreen:
    def __init__(self, root, callback_sucesso):
        self.root = root
        self.callback_sucesso = callback_sucesso
        self.root.title("Sistema de Pagamento")
        self.root.geometry("360x500")
        self.root.resizable(False, False)
        centralizar_janela(self.root)
        preparar_janela(self.root, 400, 520)

        self.build()

    def build(self):
        # ---------- LOGO ----------
        if os.path.exists(resource_path("img/logo_empresa.png")):
            img = Image.open(resource_path("img/logo_empresa.png")).resize((350, 180))
            self.logo = ImageTk.PhotoImage(img)
            tk.Label(self.root,image=self.logo).pack(pady=(30, 20))

    
        # ---------- USUÁRIO ----------
        tk.Label(self.root, text="Usuário", bg="#f2f4f8", fg="#555").pack(anchor="w", padx=60)
        frame_user, self.ent_user = entry_rounded(self.root)
        frame_user.pack(padx=60, pady=(0, 12))
        self.ent_user.focus()


        # ---------- SENHA ----------
        tk.Label(self.root, text="Senha", bg="#f2f4f8", fg="#555").pack(anchor="w", padx=60)
        frame_pass, self.ent_pass = entry_rounded(self.root, show="*")
        frame_pass.pack(padx=60, pady=(0, 10))

        icon_eye = ImageTk.PhotoImage(Image.open(resource_path("img/icon_eye.png")).resize((18, 18)))
        icon_eye_off = ImageTk.PhotoImage(Image.open(resource_path("img/icon_eye_off.png")).resize((18, 18)))

        mostrar = False

        def toggle_senha():
            nonlocal mostrar
            mostrar = not mostrar
            self.ent_pass.config(show="" if mostrar else "*")
            btn_eye.config(image=icon_eye_off if mostrar else icon_eye)
        
        btn_eye = tk.Button(frame_pass,image=icon_eye,bd=0,bg="white",activebackground="white",cursor="hand2",command=toggle_senha)
        btn_eye.image = icon_eye  # mantém referência
        btn_eye.place(x=250, y=6)



        # ---------- BOTÃO LOGIN ----------
        btn_login = tk.Button(self.root,text="ENTRAR",bg="#1976d2",fg="white",font=("Segoe UI", 10,'bold'),relief="flat",cursor="hand2",command=self.autenticar)
        btn_login.pack(fill="x", padx=60, pady=(10, 20))

        btn_login.bind("<Enter>", lambda e: btn_login.config(bg="#1565c0"))
        btn_login.bind("<Leave>", lambda e: btn_login.config(bg="#1976d2"))

        # ---------- VERSÃO ----------
        tk.Label(self.root, text=f"Versão {APP_VERSION}", bg="#f2f4f8", fg="#888", font=("Segoe UI", 8)).pack(pady=(0, 10))
        tk.Label(self.root, text="© 2026 Desenvolvido por Fabricio Lami", bg="#f2f4f8", fg="#888", font=("Segoe UI", 8)).pack()

        # Enter para logar
        self.root.bind("<Return>", lambda e: self.autenticar())

    def autenticar(self):
        try:
            conn = db.get_conn()
            c = conn.cursor()

            c.execute(
                "SELECT login, perfil FROM usuarios WHERE login=%s AND senha=%s",
                (self.ent_user.get(), self.ent_pass.get())
            )
            res = c.fetchone()
            conn.close()

        except Exception as e:
            logging.critical(f"ERRO BANCO: {e}")
            messagebox.showerror(
                "Banco indisponível",
                "Não foi possível conectar ao banco.\nTente novamente mais tarde."
            )
            return

        if res:
            for widget in self.root.winfo_children():
                widget.destroy()
            self.callback_sucesso(res[0], res[1])
        else:
            messagebox.showerror("Erro", "Login ou senha incorretos")

