# view/main_app.py
from utils.alerts import alert
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import qrcode
from PIL import ImageTk
import pandas as pd


from db import get_conn
from db import buscar_configs
from db import salvar_configs
from models import Funcionario 
from services.pix_service import gerar_payload_pix # Importando do novo serviço
from styles import BTN_VERDE, BTN_AZUL, BTN_ROXO, BTN_PADRAO, BTN_VERMELHO
from styles import add_hover

    # ================= APP ================= #

class App:
    def __init__(self, root, perfil):
        self.root = root
        self.perfil = perfil
        root.title(f"Sistema Financeiro - {perfil}")
        root.geometry("1300x750")

        self.vars = {k: tk.StringVar() for k in
                     ["nome", "admissao", "banco", "pix", "salario", "adiant", "va"]}

        self.func_edit = None

        self.build()
        self.load_table()
        self.aplicar_permissoes()

    # ---------- UI ---------- #

    # ---------- PERÍODO DE PAGAMENTO ----------
    def build(self):    
        periodo = tk.LabelFrame(self.root, text="Período de Pagamento", padx=10, pady=5)
        periodo.pack(fill="x", padx=10, pady=5)

        tk.Label(periodo, text="Mês").pack(side="left")
        self.ent_mes_pgto = tk.Entry(periodo, width=5)
        self.ent_mes_pgto.pack(side="left", padx=5)

        tk.Label(periodo, text="Ano").pack(side="left")
        self.ent_ano_pgto = tk.Entry(periodo, width=8)
        self.ent_ano_pgto.pack(side="left", padx=5)

        # valor padrão = mês atual
        hoje = datetime.now()
        self.ent_mes_pgto.insert(0, str(hoje.month))
        self.ent_ano_pgto.insert(0, str(hoje.year))

        # ---- CONFIGURAÇÃO DE DIAS DE PAGAMENTO ----
        tk.Label(periodo, text="Dia Salário").pack(side="left", padx=(15, 2))
        self.ent_dia_sal = tk.Entry(periodo, width=4)
        self.ent_dia_sal.pack(side="left", padx=5)

        tk.Label(periodo, text="Dia Adiant.").pack(side="left", padx=(10, 2))
        self.ent_dia_adiant = tk.Entry(periodo, width=4)
        self.ent_dia_adiant.pack(side="left", padx=5)

        self.btn_salvar_datas = tk.Button(periodo, text="Salvar Datas", command=self.salvar_datas_pgto)
        self.btn_salvar_datas.pack(side="left", padx=15)

        cfg = buscar_configs()
        if cfg:
            self.ent_dia_sal.insert(0, str(cfg[0]))
            self.ent_dia_adiant.insert(0, str(cfg[1]))
        
        if self.perfil.lower() != "master":
            self.ent_dia_sal.config(state="disabled")
            self.ent_dia_adiant.config(state="disabled")
            self.btn_salvar_datas.config(state="disabled")

        # ---------- FORMULÁRIO ----------
        form = tk.LabelFrame(self.root, text="Funcionário", padx=10, pady=10)
        form.pack(fill="x", padx=10, pady=5)

        labels = [
            ("Nome", "nome"),
            ("Admissão", "admissao"),
            ("Banco", "banco"),
            ("Chave PIX", "pix"),
            ("Salário", "salario"),
            ("Adiantamento", "adiant"),
            ("VA", "va"),
        ]

        for i, (lbl, var) in enumerate(labels):
            tk.Label(form, text=lbl).grid(row=0, column=i * 2)
            tk.Entry(form, textvariable=self.vars[var], width=15).grid(row=0, column=i * 2 + 1)

        # frame de ações do formulário
        actions_form = tk.Frame(form)
        actions_form.grid(row=0, column=14, columnspan=6, padx=(30, 0), sticky="e")

        self.btn_save = tk.Button(actions_form, text="Salvar", command=self.save, **BTN_VERDE)
        self.btn_save.pack(side="left", padx=5)
        add_hover(self.btn_save, bg_hover="#1d8d4c")

        self.btn_edit = tk.Button(actions_form, text="Editar", command=self.edit, **BTN_PADRAO)
        self.btn_edit.pack(side="left", padx=5)
        add_hover(self.btn_edit, bg_hover="#a7a7a7")

        self.btn_delete = tk.Button(actions_form, text="Excluir", command=self.delete, **BTN_VERMELHO)
        self.btn_delete.pack(side="left", padx=5)
        add_hover(self.btn_delete, bg_hover="#c43020")

        cols = ("ID", "Nome", "Banco", "Salário", "VA", "Adiant.", "Total")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c, command=lambda col=c: self.sort_tree(col, False))
            self.tree.column(c, width=150, anchor="center")
            self.tree.pack(fill="both", expand=True, padx=10, pady=5)


        btns = tk.Frame(self.root)
        btns.pack(pady=15)

        btn_pix = tk.Button(btns, text="Gerar PIX", command=self.pix, width=10, **BTN_VERDE)
        btn_pix.pack(side="left", padx=10)
        add_hover(btn_pix, bg_hover="#27ae60")

        btn_pago = tk.Button(btns, text="Marcar Pago", command=self.mark_paid, **BTN_AZUL)
        btn_pago.pack(side="left", padx=10)
        add_hover(btn_pago, bg_hover="#2980b9")

        btn_rel = tk.Button(btns, text="Relatórios", command=self.reports, **BTN_ROXO)
        btn_rel.pack(side="left", padx=10)
        add_hover(btn_rel, bg_hover="#8e44ad")

    def salvar_datas_pgto(self):
        try:
            dia_sal = int(self.ent_dia_sal.get())
            dia_adiant = int(self.ent_dia_adiant.get())
        except ValueError:
            alert("Erro", "Os dias devem ser números inteiros")
            return

        if not (1 <= dia_sal <= 31 and 1 <= dia_adiant <= 31):
            alert("Erro", "Os dias devem estar entre 1 e 31")
            return

        salvar_configs(dia_sal, dia_adiant)
        alert("Sucesso", "Datas de pagamento salvas com sucesso")

    def aplicar_permissoes(self):
        if self.perfil != "Master":
            self.btn_delete.config(state="disabled")
            self.btn_edit.config(state="disabled")

    # ---------- CRUD ---------- #

    def load_table(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome, banco, salario_liquido, va, adiantamento FROM funcionarios WHERE ativo = TRUE ORDER BY nome")
        for r in c.fetchall():
            total = r[3] + r[4]
            self.tree.insert("", "end", values=(
                r[0], r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.2f}", f"{r[5]:.2f}", f"{total:.2f}"
            ))
        conn.close()

    def save(self):
        f = self.func_edit or Funcionario()
        f.nome = self.vars["nome"].get()
        f.admissao = self.vars["admissao"].get()
        f.banco = self.vars["banco"].get()
        f.chave_pix = self.vars["pix"].get()
        f.salario = float(self.vars["salario"].get())
        f.adiantamento = float(self.vars["adiant"].get())
        f.va = float(self.vars["va"].get())
        f.salvar()
        self.func_edit = None
        self.clear()
        self.load_table()

    def clear(self):
        for v in self.vars.values():
            v.set("")

    def edit(self):
        sel = self.tree.selection()
        if not sel:
            return
        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)
        self.func_edit = f
        self.vars["nome"].set(f.nome)
        self.vars["admissao"].set(f.admissao)
        self.vars["banco"].set(f.banco)
        self.vars["pix"].set(f.chave_pix)
        self.vars["salario"].set(f.salario)
        self.vars["adiant"].set(f.adiantamento)
        self.vars["va"].set(f.va)
        

    def delete(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("Atenção", "Selecione um funcionário.")
            return

        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)

        if not messagebox.askyesno(
            "Confirmar",
            f"Deseja desativar o funcionário:\n\n{f.nome}?\n\n"
            "O histórico de pagamentos será mantido."
        ):
            return

        Funcionario.excluir(fid)
        self.load_table()

        messagebox.showinfo(
            "OK",
            "Funcionário desativado com sucesso.\n"
            "O histórico foi preservado."
        )

    def sort_tree(self, col, reverse):
        dados = [(self.tree.set(k, col), k) for k in self.tree.get_children("")]

        # tenta converter para número
        try:
            dados = [(float(v.replace("R$", "").replace(",", "").strip()), k) for v, k in dados]
        except:
            dados = [(v.lower(), k) for v, k in dados]

        dados.sort(reverse=reverse)

        for i, (_, k) in enumerate(dados):
            self.tree.move(k, "", i)

        # inverte a próxima ordenação
        self.tree.heading(col, command=lambda: self.sort_tree(col, not reverse))


    # ---------- PIX ---------- #

    def pix(self):
        sel = self.tree.selection()
        if not sel:
            alert("aviso", "Selecione um funcionário para gerar o PIX.")
            return

        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)

        win = tk.Toplevel(self.root)
        win.title("Gerar PIX")
        win.geometry("350x220")
        win.resizable(False, False)

        container = tk.Frame(win, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(
            container,
            text=f"Funcionário: {f.nome}",
            font=("Segoe UI", 10, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # Nenhuma opção selecionada por padrão
        tipo_pgto = tk.StringVar(value="")

        tk.Label(container, text="Tipo de pagamento:").pack(anchor="w")

        rb_sal = tk.Radiobutton(
            container,
            text="Salário + VA",
            variable=tipo_pgto,
            value="sal"
    )
        rb_sal.pack(anchor="w", pady=2)

        rb_adi = tk.Radiobutton(
            container,
            text="Adiantamento",
            variable=tipo_pgto,
            value="adiant"
        )
        rb_adi.pack(anchor="w", pady=2)

        def gerar_pix():
            if not tipo_pgto.get():
                alert("aviso", "Selecione o tipo de pagamento antes de gerar o PIX.")
                return

            if tipo_pgto.get() == "sal":
                valor = f.salario + f.va
                tipo = "SAL"
            else:
                valor = f.adiantamento
                tipo = "ADI"

            mes = self.ent_mes_pgto.get()
            ano = self.ent_ano_pgto.get()

            if not mes or not ano:
                alert("erro", "Informe o mês e o ano do pagamento.")
                return

            try:
                mes_int = int(mes)
                ano_int = int(ano)
            except ValueError:
                alert("erro", "Mês ou ano inválido.")
                return

            if mes_int < 1 or mes_int > 12:
                alert("erro", "Mês deve estar entre 1 e 12.")
                return

            data = f"{ano_int}{mes_int:02}01"
            txid = f"{tipo}{data}{f.id}"

            payload = gerar_payload_pix(
                f.chave_pix,
                valor,
                f.nome,
                txid
            )

            win.destroy()
            descricao = "Salário + VA" if tipo_pgto.get() == "sal" else "Adiantamento Salarial"
            self.mostrar_qr_code(payload,f.nome,valor,descricao)


        tk.Button(container, text="Gerar PIX", command=gerar_pix, **BTN_VERDE).pack(pady=15)

    def mostrar_qr_code(self, payload, nome, valor, descricao):
        win = tk.Toplevel(self.root)
        win.title("PIX Gerado")
        win.geometry("350x450")
        win.resizable(False, False)

        container = tk.Frame(win, padx=15, pady=15)
        container.pack(fill="both", expand=True)

        # Nome do funcionário
        tk.Label(container, text=nome,font=("Segoe UI", 12, "bold")).pack(pady=(0, 3))

        # Tipo de pagamento
        tk.Label(container, text=descricao, font=("Segoe UI", 10)).pack(pady=(0, 10))

        # QR Code
        img = qrcode.make(payload)
        img = img.resize((300, 300))  # controle explícito
        img_tk = ImageTk.PhotoImage(img)

        qr_frame = tk.Frame(container)
        qr_frame.pack(pady=5)

        lbl_qr = tk.Label(container, image=img_tk)
        lbl_qr.image = img_tk  # evita garbage collection
        lbl_qr.pack()

        # Valor
        valor_fmt = f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        tk.Label(container, text=f"Valor: {valor_fmt}", font=("Segoe UI", 12, "bold")).pack(pady=(10, 5))
        tk.Label(container, text="Escaneie o QR Code para pagamento", font=("Segoe UI", 10)).pack()

    # ---------- PAGAMENTO ---------- #

    def mark_paid(self):
        if self.perfil != "Master":
            messagebox.showerror("Acesso negado", "Somente Master pode marcar pagamento")
            return

        sel = self.tree.selection()
        if not sel:
            return

        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)

        tipo = "Salário+VA"
        valor = f.salario + f.va

        data_pagamento = datetime.now()
        mes = data_pagamento.month
        ano = data_pagamento.year

        conn = get_conn()
        cur = conn.cursor()

    # -- BLOQUEIO DE DUPLICIDADE
        cur.execute("""
            SELECT 1
            FROM historico_pagamentos
            WHERE funcionario_id = %s
            AND tipo = %s
            AND mes = %s
            AND ano = %s
        """, (fid, tipo, mes, ano))


        if cur.fetchone():
            messagebox.showwarning(
                "Pagamento duplicado",
                "Este pagamento já foi registrado neste mês."
            )
            conn.close()
            return

    # -- INSERIR
        cur.execute("""
            INSERT INTO historico_pagamentos
                (funcionario_id, data, tipo, valor, mes, ano)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            fid,
            data_pagamento.date(),
            tipo,
            valor,
            mes,
            ano
        ))

        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Pagamento registrado com sucesso")


    # ---------- RELATÓRIOS ---------- #

    def reports(self):
        win = tk.Toplevel(self.root)
        win.title("Relatório Mensal")
        win.geometry("1200x620")

    # ---------- FILTROS ----------
        frame_filtro = tk.Frame(win)
        frame_filtro.pack(fill="x", padx=10, pady=5)

        tk.Label(frame_filtro, text="Mês").pack(side="left")
        ent_mes = tk.Entry(frame_filtro, width=5)
        ent_mes.pack(side="left", padx=5)
        ent_mes.focus_set()

        tk.Label(frame_filtro, text="Ano").pack(side="left")
        ent_ano = tk.Entry(frame_filtro, width=8)
        ent_ano.pack(side="left", padx=5)
        
        hoje = datetime.now()
        ent_mes.insert(0, str(hoje.month))
        ent_ano.insert(0, str(hoje.year))

    # ---------- TABELA ----------
        cols = ("pid", "nome", "tipo", "valor", "mes", "ano")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        titulos = ["ID Pgto", "Funcionário", "Tipo", "Valor", "Mês", "Ano"]

        for c, t in zip(cols, titulos):
            tree.heading(c, text=t)
            tree.column(c, anchor="center", width=180)
            tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- TOTALIZADORES ----------
        lbl_totais = tk.Label(win, text="", font=("Arial", 10, "bold"))
        lbl_totais.pack(pady=5)

        dados_cache = []

    # ---------- FILTRAR ----------
        def filtrar():
            tree.delete(*tree.get_children())
            dados_cache.clear()

            mes_txt = ent_mes.get().strip()
            ano_txt = ent_ano.get().strip()

            if not mes_txt or not ano_txt:
                messagebox.showwarning("Atenção", "Informe mês e ano")
                return

            try:
                mes = int(mes_txt)
                ano = int(ano_txt)
            except ValueError:
                messagebox.showerror("Erro", "Mês e ano devem ser números")
                return

            if mes < 1 or mes > 12:
                messagebox.showerror("Erro", "Mês inválido (1 a 12)")
                return

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("""
                SELECT
                    h.id,
                    f.nome,
                    h.tipo,
                    h.valor,
                    h.mes,
                    h.ano
                FROM historico_pagamentos h
                JOIN funcionarios f ON f.id = h.funcionario_id
                WHERE h.mes = %s
                AND h.ano = %s
                ORDER BY f.nome
            """, (mes, ano))

            rows = cur.fetchall()
            conn.close()

            total_sal = total_adi = total_geral = 0

            for r in rows:
                salario = float(r[2] or 0)
                adiant = float(r[3] or 0)
                total = salario + adiant

                total_sal += salario
                total_adi += adiant
                total_geral += total

                tree.insert("", "end", values=(
                    r[0],
                    r[1],
                    f"R$ {salario:.2f}",
                    f"R$ {adiant:.2f}",
                    f"R$ {total:.2f}"
            ))


                dados_cache.append([r[0], r[1], salario, adiant, total])

            lbl_totais.config(
                text=(
                    f"Total Salários: R$ {total_sal:.2f}    "
                    f"Total Adiantamentos: R$ {total_adi:.2f}    "
                    f"Total Geral: R$ {total_geral:.2f}"
        )
    )


    # ---------- EXPORTAR EXCEL ----------
        def exportar_excel():
            if not dados_cache:
                messagebox.showwarning("Atenção", "Nenhum dado para exportar")
                return

            caminho = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")]
            )

            if not caminho:
                return

            df = pd.DataFrame(
                dados_cache,
                columns=["ID", "Funcionário", "Salário", "Adiantamento", "Total"]
            )
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Sucesso", "Excel gerado com sucesso")

    # ---------- EXPORTAR PDF ----------
        def exportar_pdf():
            if not dados_cache:
                messagebox.showwarning("Atenção", "Nenhum dado para exportar")
                return

            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")]
            )

            if not caminho:
                return

            from reportlab.lib.pagesizes import A4
            from reportlab.pdfgen import canvas

            c = canvas.Canvas(caminho, pagesize=A4)
            y = 800

            c.setFont("Helvetica-Bold", 12)
            c.drawString(40, y, "Relatório Mensal de Pagamentos")
            y -= 30

            c.setFont("Helvetica", 9)
            for d in dados_cache:
                c.drawString(
                    40, y,
                    f"{d[1]} | Salário: R$ {d[2]:.2f} | "
                    f"Adiant.: R$ {d[3]:.2f} | Total: R$ {d[4]:.2f}"
            )
                y -= 15
                if y < 40:
                    c.showPage()
                    y = 800

            c.save()
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso")

        def excluir_pagamento():
            if self.perfil != "Master":
                messagebox.showerror("Permissão negada", "Apenas o Master pode excluir pagamentos.")
                return

            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione um pagamento")
                return

            pid = tree.item(sel)["values"][0]

            confirmar = messagebox.askyesno(
                "Confirmar exclusão",
                "Tem certeza que deseja excluir este pagamento?\nEssa ação não pode ser desfeita."
            )

            if not confirmar:
                return

            conn = get_conn()
            cur = conn.cursor()
            cur.execute("DELETE FROM historico_pagamentos WHERE id = %s", (pid,))
            conn.commit()
            conn.close()

            tree.delete(sel)
            messagebox.showinfo("Sucesso", "Pagamento excluído com sucesso")    

    # ---------- BOTÕES ----------
        frame_botoes = tk.Frame(win)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Filtrar", bg="#3498db", command=filtrar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Exportar Excel", bg="#2ecc71", command=exportar_excel).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Exportar PDF", bg="#9b59b6", command=exportar_pdf).pack(side="left", padx=5)
        tk.Button(frame_botoes,text="Excluir Pagamento",bg="#b92717",fg="white",command=excluir_pagamento).pack(side="left", padx=5)

        filtrar()