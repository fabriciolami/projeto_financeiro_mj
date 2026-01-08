# views/main_app.py
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import qrcode
from PIL import ImageTk
import pandas as pd

# Importações ajustadas para a nova estrutura
from db import get_conn 
from models.models import Funcionario 
from services.pix_service import gerar_payload_pix # Importando do novo serviço


    # ================= APP ================= #

class App:
    def __init__(self, root, perfil):
        self.root = root
        self.perfil = perfil
        root.title(f"Sistema Financeiro - {perfil}")
        root.geometry("1200x700")

        self.vars = {k: tk.StringVar() for k in
                     ["nome", "admissao", "banco", "pix", "salario", "adiant", "va"]}

        self.func_edit = None

        self.build()
        self.load_table()
        self.aplicar_permissoes()

    # ---------- UI ---------- #

        # ---------- PERÍODO DE PAGAMENTO ----------
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


    def build(self):
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

        self.btn_save = tk.Button(form, text="Salvar", command=self.save)
        self.btn_save.grid(row=1, column=0, columnspan=14, pady=10)

        cols = ("ID", "Nome", "Banco", "Salário", "VA", "Adiant.", "Total")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c)
            self.tree.column(c, width=150, anchor="center")

        self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        btns = tk.Frame(self.root)
        btns.pack(pady=10)

        tk.Button(btns, text="Editar", command=self.edit).pack(side="left", padx=5)
        tk.Button(btns, text="Excluir", command=self.delete).pack(side="left", padx=5)
        tk.Button(btns, text="Gerar PIX", command=self.pix).pack(side="left", padx=5)
        tk.Button(btns, text="Marcar Pago", command=self.mark_paid).pack(side="left", padx=5)
        tk.Button(btns, text="Relatórios", command=self.reports).pack(side="left", padx=5)

    # ---------- CRUD ---------- #

    def load_table(self):
        self.tree.delete(*self.tree.get_children())
        conn = get_conn()
        c = conn.cursor()
        c.execute("SELECT id, nome, banco, salario_liquido, va, adiantamento FROM funcionarios")
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
        if self.perfil != "Master":
            return
        
        sel = self.tree.selection()
        if not sel:
            return
        fid = self.tree.item(sel)["values"][0]
        conn = get_conn()
        c = conn.cursor()
        c.execute("DELETE FROM funcionarios WHERE id=%s", (fid,))
        conn.commit()
        conn.close()
        self.load_table()

    def aplicar_permissoes(self):
        if self.perfil == "Financeiro":
            self.btn_salvar.config(state="disabled")

    # ---------- PIX ---------- #

def pix(self):
    sel = self.tree.selection()
    if not sel:
        return
    fid = self.tree.item(sel)["values"][0]
    f = Funcionario.buscar_por_id(fid)

    win = tk.Toplevel(self.root)
    win.title("Tipo de Pagamento")

    opt = tk.StringVar(value="sal")

    tk.Radiobutton(win, text="Salário + VA", variable=opt, value="sal").pack(anchor="w")
    tk.Radiobutton(win, text="Adiantamento", variable=opt, value="adiant").pack(anchor="w")

    def gerar():
        valor = f.salario + f.va if opt.get() == "sal" else f.adiantamento
        tipo = "SAL" if opt.get() == "sal" else "ADI"

        mes = self.ent_mes_pgto.get()
        ano = self.ent_ano_pgto.get()

        if not mes or not ano:
            messagebox.showerror("Erro", "Informe o mês e o ano do pagamento")
            return

        try:
            mes_int = int(mes)
            ano_int = int(ano)
        except ValueError:
            messagebox.showerror("Erro", "Mês/Ano inválidos")
            return

        if mes_int < 1 or mes_int > 12:
            messagebox.showerror("Erro", "Mês inválido (1 a 12)")
            return

        # data lógica para o PIX (não precisa ser dia real)
        data = f"{ano_int}{mes_int:02}01"

        txid = f"{tipo}{data}{f.id}"

        payload = gerar_payload_pix(
            f.chave_pix,
            valor,
            f.nome,
            txid
    )

        img = qrcode.make(payload).resize((300, 300))
        imgtk = ImageTk.PhotoImage(img)
        qr = tk.Toplevel(self.root)
        tk.Label(qr, image=imgtk).pack()
        qr.image = imgtk

        tk.Button(win, text="Gerar QR Code", command=gerar).pack(pady=10)

    # ---------- PAGAMENTO ---------- #

    def mark_paid(self):
        sel = self.tree.selection()
        if not sel:
            return
        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)

        valor = f.salario + f.va
        tipo = "Salário+VA"

        conn = get_conn()
        c = conn.cursor()
        hoje = datetime.now()
        mes = hoje.month
        ano = hoje.year

        c.execute("""
            INSERT INTO historico_pagamentos
            (funcionario_id, data, mes, ano, tipo, valor)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            fid,
            hoje.date(),
            str(mes),   # mantém compatível com coluna TEXT
            str(ano),
            tipo,
            valor
))

        conn.commit()
        conn.close()

        messagebox.showinfo("OK", "Pagamento registrado")

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

    # ---------- TABELA ----------
        cols = ("id", "nome", "salario", "adiant", "total")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        for c, t in zip(
            cols,
            ["ID", "Funcionário", "Salário", "Adiantamento", "Total no mês"]
        ):
            tree.heading(c, text=t)
            tree.column(c, anchor="center", width=200)

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
                    f.id,
                    f.nome,
                    COALESCE(SUM(CASE WHEN h.tipo='Salário+VA' THEN h.valor END), 0),
                    COALESCE(SUM(CASE WHEN h.tipo='Adiantamento' THEN h.valor END), 0)
                FROM historico_pagamentos h
                JOIN funcionarios f ON f.id = h.funcionario_id
                WHERE h.mes::int = %s
                AND h.ano::int = %s
                GROUP BY f.id, f.nome
                ORDER BY f.nome
            """, (mes, ano))

            rows = cur.fetchall()
            conn.close()

            total_sal = total_adi = total_geral = 0

            for r in rows:
                salario = r[2]
                adiant = r[3]
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
                    f"Total Salários: R$ {total_sal:.2f} | "
                    f"Total Adiantamentos: R$ {total_adi:.2f} | "
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

    # ---------- BOTÕES ----------
        frame_botoes = tk.Frame(win)
        frame_botoes.pack(pady=10)

        tk.Button(frame_botoes, text="Filtrar", command=filtrar).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Exportar Excel", command=exportar_excel).pack(side="left", padx=5)
        tk.Button(frame_botoes, text="Exportar PDF", command=exportar_pdf).pack(side="left", padx=5)