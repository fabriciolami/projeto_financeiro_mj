import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import sqlite3
import qrcode
from PIL import ImageTk, Image
from datetime import datetime
import os
import re
import pandas as pd  # Necessário para exportar para Excel/CSV
from models import Funcionario

# --- FUNÇÕES DE UTILIDADE ---


def limpar_moeda(valor):
    if valor is None or valor == "":
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    valor = str(valor)
    valor = valor.replace("R$", "").replace(" ", "")
    valor = valor.replace(".", "").replace(",", ".")

    try:
        return float(valor)
    except ValueError:
        return 0.0


def crc16(payload):
    crc = 0xFFFF
    for char in payload:
        crc ^= ord(char) << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return f"{crc:04X}"


def gerar_payload_pix(chave, valor, nome_favorecido):
    nome = nome_favorecido[:25].upper()
    valor_str = f"{valor:.2f}"

    gui = "BR.GOV.BCB.PIX"
    campo_gui = f"0014{gui}"
    campo_chave = f"01{len(chave):02}{chave}"

    merchant_account = campo_gui + campo_chave
    merchant_account_len = f"{len(merchant_account):02}"

    # Campo adicional com TXID fixo
    txid = "PAGAMENTO001"
    campo_txid = f"05{len(txid):02}{txid}"
    campo_62 = f"62{len(campo_txid):02}{campo_txid}"

    payload = (
        "000201"
        f"26{merchant_account_len}{merchant_account}"
        "52040000"
        "5303986"
        f"54{len(valor_str):02}{valor_str}"
        "5802BR"
        f"59{len(nome):02}{nome}"
        "6008BRASILIA"
        f"{campo_62}"
        "6304"
    )

    payload += crc16(payload)
    return payload


# --- BANCO DE DADOS ---


def iniciar_db():
    conn = sqlite3.connect('folha_pagamentos.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS funcionarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT, nome TEXT, admissao TEXT, banco TEXT, 
        chave_pix TEXT, salario_liquido REAL, va REAL, adiantamento REAL, status TEXT DEFAULT 'Pendente')''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS historico_pagamentos (
        id INTEGER PRIMARY KEY AUTOINCREMENT, funcionario_id INTEGER, nome TEXT, 
        valor REAL, tipo TEXT, data_pagamento TEXT, mes TEXT, ano TEXT)''')
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS configs (id INTEGER PRIMARY KEY, dia_adiantamento TEXT, dia_salario TEXT)''')
    cursor.execute("SELECT * FROM configs")
    if not cursor.fetchall():
        cursor.execute(
            "INSERT INTO configs (id, dia_adiantamento, dia_salario) VALUES (1, '20', '5')")
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY AUTOINCREMENT, login TEXT, senha TEXT, perfil TEXT)''')
    cursor.execute("SELECT * FROM usuarios")
    if not cursor.fetchall():
        cursor.execute(
            "INSERT INTO usuarios (login, senha, perfil) VALUES ('admin', 'admin123', 'Master'), ('fin', 'fin123', 'Financeiro')")
    conn.commit()
    conn.close()

# --- TELA DE LOGIN ---


class LoginScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema Financeiro da Marmoraria Jardim")
        self.root.geometry("400x500")

        self.caminho_logo = "img/logo_empresa.png"
        if os.path.exists(self.caminho_logo):
            img = Image.open(self.caminho_logo).resize(
                (450, 250), Image.Resampling.LANCZOS)
            self.logo_tk = ImageTk.PhotoImage(img)
            tk.Label(root, image=self.logo_tk).pack(pady=20)
        else:
            tk.Label(root, text="[ LOGO DA EMPRESA ]", font=(
                "Arial", 12, "bold"), pady=40).pack()

        tk.Label(root, text="Usuário:").pack()
        self.ent_user = tk.Entry(root, width=25)
        self.ent_user.pack(pady=5)
        tk.Label(root, text="Senha:").pack()
        self.ent_pass = tk.Entry(root, show="*", width=25)
        self.ent_pass.pack(pady=5)
        ttk.Button(
            root,
            text="Entrar",
            command=self.autenticar,
            style="Primary.TButton"
        ).pack(pady=30)

    def autenticar(self):
        u, s = self.ent_user.get(), self.ent_pass.get()
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute("SELECT perfil FROM usuarios WHERE login=? AND senha=?", (u, s))
        res = c.fetchone()
        conn.close()
        if res:
            self.root.destroy()
            main_root = tk.Tk()
            AppFolha(main_root, res[0])
            main_root.mainloop()
        else:
            messagebox.showerror("Erro", "Login ou senha incorretos")

# --- APP PRINCIPAL ---


class AppFolha:
    def __init__(self, root, perfil):
        self.root = root
        self.perfil = perfil
        self.root.title(f"Sistema Financeiro - {self.perfil}")
        self.root.geometry("1200x700")
        self.id_selecionado = None
        self.vars = {k: tk.StringVar() for k in [
            'nome', 'admissao', 'banco', 'pix', 'salario', 'adiantamento', 'va']}

        self.criar_layout()
        self.atualizar_tabela()
        self.aplicar_permissoes()

    def criar_layout(self):
        frame_h = tk.Frame(self.root, bg="#ecf0f1", pady=5)
        frame_h.pack(fill="x", padx=20)
        tk.Label(frame_h, text=f"Perfil: {self.perfil}", bg="#ecf0f1", font=(
            "Arial", 9, "bold")).pack(side="left")
        self.lbl_sugestao = tk.Label(
            frame_h, text="", bg="#ecf0f1", fg="#c0392b", font=("Arial", 9, "bold"))
        self.lbl_sugestao.pack(side="left", padx=50)
        self.checar_datas_pagamento()
        tk.Button(frame_h, text="Log Out", command=self.logout,
                  bg="#95a5a6").pack(side="right")

        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=10)

        self.aba_func = tk.Frame(self.notebook)
        self.notebook.add(self.aba_func, text=" 👥 Colaboradores ")
        self.montar_aba_funcionarios()

        if self.perfil == "Master":
            self.aba_users = tk.Frame(self.notebook)
            self.notebook.add(self.aba_users, text=" 👤 Gerenciar Usuários ")
            self.montar_aba_usuarios()

            def buscar_funcionario_por_id(self, funcionario_id):
                conn = sqlite3.connect('folha_pagamentos.db')
                c = conn.cursor()

                c.execute("""
                SELECT nome, admissao, banco, chave_pix,
                    salario_liquido, adiantamento, va
                FROM funcionarios
                WHERE id = ?
                """, (funcionario_id,))

                dados = c.fetchone()
                conn.close()
                return dados

    def montar_aba_funcionarios(self):
        if self.perfil == "Master":
            frame_cfg = tk.LabelFrame(
                self.aba_func, text=" Configuração de Dias de Pagamento ")
            frame_cfg.pack(fill="x", padx=10, pady=5)
            tk.Label(frame_cfg, text="Dia Vale:").grid(row=0, column=0, padx=5)
            self.ent_dia_adv = tk.Entry(frame_cfg, width=5)
            self.ent_dia_adv.grid(row=0, column=1)
            tk.Label(frame_cfg, text="Dia Salário:").grid(
                row=0, column=2, padx=5)
            self.ent_dia_sal = tk.Entry(frame_cfg, width=5)
            self.ent_dia_sal.grid(row=0, column=3)
            tk.Button(frame_cfg, text="Salvar Dias", command=self.salvar_configs).grid(
                row=0, column=4, padx=10)
            self.carregar_configs()

        self.frame_in = tk.LabelFrame(
            self.aba_func, text=" Cadastro / Edição ", padx=10, pady=10)
        self.frame_in.pack(fill="x", padx=10, pady=10)
        campos = [("Nome:", 'nome'), ("Admissão:", 'admissao'), ("Banco:", 'banco'),
                  ("Chave PIX:", 'pix'), ("Salário R$:", 'salario'), ("Adiant. (Vale) R$:", 'adiantamento'), ("VA R$:", 'va')]
        for i, (l, v) in enumerate(campos):
            tk.Label(self.frame_in, text=l).grid(row=0, column=i*2, padx=2)
            tk.Entry(self.frame_in, textvariable=self.vars[v], width=15).grid(
                row=0, column=i*2+1)

        self.btn_salvar = tk.Button(
            self.frame_in, text="Salvar Funcionário", command=self.salvar, bg="#2e9acc", fg="white")
        self.btn_salvar.grid(row=1, column=0, columnspan=14,
                             pady=10, sticky="nsew")

        # TABELA SEM A COLUNA STATUS
        cols = ("ID", "Nome", "Admissão", "Banco", "Chave PIX",
                "Salário", "Adiant.", "VA", "Total")
        self.tree = ttk.Treeview(self.aba_func, columns=cols, show="headings")
        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=120, anchor="center")
        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        frame_ac = tk.Frame(self.aba_func)
        frame_ac.pack(fill="x", padx=10, pady=10)
        tk.Button(frame_ac, text="🖼️ GERAR PIX", command=self.abrir_janela_qr,
                  bg="#3498db", fg="white", width=15).pack(side="left", padx=5)
        tk.Button(frame_ac, text="✅ MARCAR PAGO", command=self.marcar_pago,
                  bg="#27ae60", fg="white", width=18).pack(side="left", padx=5)
        self.btn_edit = tk.Button(
            frame_ac, text="✏️ Editar", command=self.preparar_edicao, width=10).pack(side="left", padx=5)
        tk.Button(frame_ac, text="📊 Relatórios", command=self.abrir_historico,
                  bg="#8e44ad", fg="white", width=15).pack(side="left", padx=20)

        self.btn_del = tk.Button(
            frame_ac, text="🗑️ Remover", command=self.remover, bg="#e74c3c", fg="white").pack(side="right")

    def montar_aba_usuarios(self):
        frame_u = tk.LabelFrame(
            self.aba_users, text=" Alterar Acessos ", padx=20, pady=20)
        frame_u.pack(pady=20, padx=20, fill="x")
        self.user_var = tk.StringVar()
        self.pass_var = tk.StringVar()
        tk.Label(frame_u, text="Novo Login:").grid(row=0, column=0, pady=5)
        tk.Entry(frame_u, textvariable=self.user_var, width=30).grid(
            row=0, column=1, pady=5, padx=10)
        tk.Label(frame_u, text="Nova Senha:").grid(row=1, column=0, pady=5)
        tk.Entry(frame_u, textvariable=self.pass_var, width=30).grid(
            row=1, column=1, pady=5, padx=10)
        tk.Button(frame_u, text="💾 Atualizar Acesso", command=self.atualizar_usuario_db,
                  bg="#2ecc71", fg="white").grid(row=2, column=1, pady=20)
        self.tree_users = ttk.Treeview(self.aba_users, columns=(
            "ID", "Login", "Perfil"), show="headings", height=5)
        for c in ["ID", "Login", "Perfil"]:
            self.tree_users.heading(c, text=c)
        self.tree_users.pack(fill="x", padx=20)
        self.tree_users.bind("<<TreeviewSelect>>", self.carregar_user_campos)
        self.atualizar_tabela_usuarios()

    # --- RELATÓRIOS E EXPORTAÇÃO ---
    def abrir_historico(self):
        jh = tk.Toplevel(self.root)
        jh.title("Relatórios Financeiros")
        jh.geometry("800x600")
        f = tk.Frame(jh)
        f.pack(pady=10)
        tk.Label(f, text="Mês (MM):").pack(side="left")
        me = tk.Entry(f, width=5)
        me.pack(side="left", padx=5)
        tk.Label(f, text="Ano (AAAA):").pack(side="left")
        an = tk.Entry(f, width=8)
        an.pack(side="left", padx=5)

        tr = ttk.Treeview(jh, columns=("ID", "Nome", "Valor",
                          "Tipo", "Data"), show="headings")
        for c in tr['columns']:
            tr.heading(c, text=c)
            tr.column(c, anchor="center")
        tr.pack(fill="both", expand=True, padx=10)

        lbl_total = tk.Label(jh, text="Total: R$ 0.00",
                             font=("Arial", 12, "bold"), pady=10)
        lbl_total.pack()

        def carregar():
            for i in tr.get_children():
                tr.delete(i)
            conn = sqlite3.connect('folha_pagamentos.db')
            c = conn.cursor()
            q = "SELECT id, nome, valor, tipo, data_pagamento FROM historico_pagamentos WHERE 1=1"
            p = []
            if me.get():
                q += " AND mes = ?"
                p.append(me.get().zfill(2))
            if an.get():
                q += " AND ano = ?"
                p.append(an.get())
            c.execute(q, p)
            soma = 0
            for r in c.fetchall():
                tr.insert("", "end", values=r)
                soma += r[2]
            lbl_total.config(text=f"Total Filtrado: R$ {soma:.2f}")
            conn.close()

        def exportar_excel():
            itens = tr.get_children()
            if not itens:
                messagebox.showwarning(
                    "Aviso", "Não há dados filtrados para exportar.")
                return

            dados = []
            for item in itens:
                dados.append(tr.item(item)['values'])

            df = pd.DataFrame(
                dados, columns=["ID", "Colaborador", "Valor (R$)", "Tipo", "Data/Hora"])
            caminho = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[
                                                   ("Arquivo CSV", "*.csv"), ("Excel", "*.xlsx")])

            if caminho:
                if caminho.endswith('.csv'):
                    df.to_csv(caminho, index=False, sep=';', encoding='latin1')
                else:
                    df.to_excel(caminho, index=False)
                messagebox.showinfo(
                    "Sucesso", "Relatório exportado com sucesso!")

        def deletar():
            if self.perfil != "Master":
                return
            s = tr.selection()
            if not s:
                return
            if messagebox.askyesno("Excluir", "Apagar permanentemente?"):
                conn = sqlite3.connect('folha_pagamentos.db')
                c = conn.cursor()
                c.execute("DELETE FROM historico_pagamentos WHERE id=?",
                          (tr.item(s)['values'][0],))
                conn.commit()
                conn.close()
                carregar()

        tk.Button(f, text="🔍 Filtrar", command=carregar,
                  bg="#3498db", fg="white").pack(side="left", padx=5)
        tk.Button(f, text="📥 Exportar para Excel", command=exportar_excel,
                  bg="#27ae60", fg="white").pack(side="left", padx=5)
        if self.perfil == "Master":
            tk.Button(f, text="🗑️ Deletar Registro", command=deletar,
                      bg="#e74c3c", fg="white").pack(side="right", padx=10)
        carregar()

    # --- DEMAIS LOGICAS ---
    def atualizar_tabela_usuarios(self):
        for i in self.tree_users.get_children():
            self.tree_users.delete(i)
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute("SELECT id, login, perfil FROM usuarios")
        [self.tree_users.insert("", "end", values=r) for r in c.fetchall()]
        conn.close()

    def carregar_user_campos(self, event):
        sel = self.tree_users.selection()
        if sel:
            self.user_var.set(self.tree_users.item(sel)['values'][1])
            self.pass_var.set("")

    def atualizar_usuario_db(self):
        sel = self.tree_users.selection()
        if not sel:
            return
        id_u = self.tree_users.item(sel)['values'][0]
        if messagebox.askyesno("Confirma", "Alterar acesso?"):
            conn = sqlite3.connect('folha_pagamentos.db')
            c = conn.cursor()
            c.execute("UPDATE usuarios SET login=?, senha=? WHERE id=?",
                      (self.user_var.get(), self.pass_var.get(), id_u))
            conn.commit()
            conn.close()
            messagebox.showinfo("OK", "Atualizado!")
            self.atualizar_tabela_usuarios()

    def checar_datas_pagamento(self):
        hoje = datetime.now().day
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute("SELECT dia_adiantamento, dia_salario FROM configs WHERE id=1")
        cfg = c.fetchone()
        conn.close()
        if cfg:
            msg = f"Vale (Dia {cfg[0]}) | Salário (Dia {cfg[1]})"
            if str(hoje) == cfg[0]:
                msg = "⚠️ HOJE É DIA DE VALE!"
            elif str(hoje) == cfg[1]:
                msg = "⚠️ HOJE É DIA DE SALÁRIO!"
            self.lbl_sugestao.config(text=msg)

    def atualizar_tabela(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute(
            "SELECT id, nome, admissao, banco, chave_pix, salario_liquido, va, adiantamento FROM funcionarios")
        for r in c.fetchall():
            total = r[5] + r[6]
            self.tree.insert("", "end", values=(
                r[0], r[1], r[2], r[3], r[4], f"{r[5]:.2f}", f"{r[7]:.2f}", f"{r[6]:.2f}", f"R$ {total:.2f}"))
        conn.close()

    def salvar(self):
        if self.perfil != "Master":
            return

        if not hasattr(self, "funcionario_em_edicao") or self.funcionario_em_edicao is None:
            funcionario = Funcionario()
        else:
            funcionario = self.funcionario_em_edicao

        funcionario.nome = self.vars['nome'].get()
        funcionario.admissao = self.vars['admissao'].get()
        funcionario.banco = self.vars['banco'].get()
        funcionario.chave_pix = self.vars['pix'].get()
        funcionario.salario = limpar_moeda(self.vars['salario'].get())
        funcionario.adiantamento = limpar_moeda(
            self.vars['adiantamento'].get())
        funcionario.va = limpar_moeda(self.vars['va'].get())

        funcionario.salvar()

        self.funcionario_em_edicao = None
        self.id_selecionado = None

        self.btn_salvar.config(text="Salvar Funcionário")
        [v.set("") for v in self.vars.values()]
        self.atualizar_tabela()

    def carregar_configs(self):
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute("SELECT dia_adiantamento, dia_salario FROM configs WHERE id=1")
        r = c.fetchone()
        if r:
            self.ent_dia_adv.insert(0, r[0])
            self.ent_dia_sal.insert(0, r[1])
        conn.close()

    def salvar_configs(self):
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()
        c.execute("UPDATE configs SET dia_adiantamento=?, dia_salario=? WHERE id=1",
                  (self.ent_dia_adv.get(), self.ent_dia_sal.get()))
        conn.commit()
        conn.close()
        messagebox.showinfo("OK", "Salvo!")
        self.checar_datas_pagamento()

    def preparar_edicao(self):
        sel = self.tree.selection()
        if not sel:
            return

        funcionario_id = self.tree.item(sel)['values'][0]

        funcionario = Funcionario.buscar_por_id(funcionario_id)
        if not funcionario:
            messagebox.showerror("Erro", "Funcionário não encontrado.")
            return

        self.funcionario_em_edicao = funcionario
        self.id_selecionado = funcionario.id  # segurança

        self.vars['nome'].set(funcionario.nome)
        self.vars['admissao'].set(funcionario.admissao)
        self.vars['banco'].set(funcionario.banco)
        self.vars['pix'].set(funcionario.chave_pix)
        self.vars['salario'].set(f"{funcionario.salario:.2f}")
        self.vars['adiantamento'].set(f"{funcionario.adiantamento:.2f}")
        self.vars['va'].set(f"{funcionario.va:.2f}")

        self.btn_salvar.config(text="Confirmar Alteração ✅")

    def marcar_pago(self):
        sel = self.tree.selection()
        if not sel:
            return
        it = self.tree.item(sel)['values']
        win = tk.Toplevel(self.root)
        win.title("Pagamento")

        def confirmar(tipo):
            valor = (float(it[5]) + float(it[7])
                     ) if tipo == "Salário" else float(it[6])
            if messagebox.askyesno("Confirmar", f"Pagar {tipo} de R$ {valor:.2f}?"):
                hj = datetime.now()
                conn = sqlite3.connect('folha_pagamentos.db')
                c = conn.cursor()
                c.execute("INSERT INTO historico_pagamentos (funcionario_id, nome, valor, tipo, data_pagamento, mes, ano) VALUES (?,?,?,?,?,?,?)",
                          (it[0], it[1], valor, tipo, hj.strftime("%d/%m/%Y %H:%M"), hj.strftime("%m"), hj.strftime("%Y")))
                conn.commit()
                conn.close()
                win.destroy()
                self.atualizar_tabela()
        tk.Button(win, text="Salário + VA", command=lambda: confirmar("Salário"),
                  width=20, bg="#2ecc71").pack(pady=10, padx=20)
        tk.Button(win, text="Vale", command=lambda: confirmar(
            "Vale"), width=20, bg="#3498db").pack(pady=10, padx=20)

    def abrir_janela_qr(self):
        sel = self.tree.selection()
        if not sel:
            return
        it = self.tree.item(sel)['values']
        win_q = tk.Toplevel(self.root)
        win_q.title("QR Code")

        def gerar(t):
            valor = (float(it[5]) + float(it[7])
                     ) if t == "Salário" else float(it[6])
            payload = gerar_payload_pix(str(it[4]), valor, it[1])
            jq = tk.Toplevel(win_q)
            jq.title(f"QR {t}")
            img = qrcode.make(payload).resize((250, 250))
            im = ImageTk.PhotoImage(img)
            lbl_img = tk.Label(jq, image=im)
            lbl_img.image = im
            lbl_img.pack(pady=10)
            tk.Label(jq, text=f"R$ {valor:.2f}", font="bold").pack()
            e = tk.Entry(jq, width=40)
            e.insert(0, payload)
            e.pack()
        tk.Button(win_q, text="QR Salário", command=lambda: gerar(
            "Salário"), width=20).pack(pady=10, padx=20)
        tk.Button(win_q, text="QR Vale", command=lambda: gerar(
            "Vale"), width=20).pack(pady=10, padx=20)

    def logout(self):
        self.root.destroy()
        n = tk.Tk()
        LoginScreen(n)
        n.mainloop()

    def remover(self):
        sel = self.tree.selection()
        if not sel or self.perfil != "Master":
            return
        if messagebox.askyesno("Excluir", "Remover colaborador?"):
            conn = sqlite3.connect('folha_pagamentos.db')
            c = conn.cursor()
            c.execute("DELETE FROM funcionarios WHERE id=?",
                      (self.tree.item(sel)['values'][0],))
            conn.commit()
            conn.close()
            self.atualizar_tabela()

    def aplicar_permissoes(self):
        if self.perfil == "Financeiro":
            self.btn_salvar.config(state="disabled")
            self.btn_del.config(state="disabled")


if __name__ == "__main__":
    iniciar_db()
    root_l = tk.Tk()
    LoginScreen(root_l)
    root_l.mainloop()
