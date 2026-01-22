# view/main_app.py
from utils.alerts import alert
import tkinter as tk
import os
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import qrcode
from PIL import ImageTk
import pandas as pd
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.lib import colors
from utils.paths import resource_path
from db import get_conn
from db import buscar_configs
from db import salvar_configs
from models import Funcionario 
from services.pix_service import gerar_payload_pix # Importando do novo serviço
from styles import BTN_VERDE, BTN_AZUL, BTN_ROXO, BTN_PADRAO, BTN_VERMELHO
from styles import add_hover
from styles import centralizar_janela
from decimal import Decimal
from utils.money import format_money
from repositories.payments_repository import PaymentsRepository
from services.financial_service import FinancialService


    # ================= APP ================= #

class App:
    def __init__(self, root, usuario, perfil):
        self.root = root
        self.usuario = usuario
        self.perfil = perfil

        hoje = datetime.now()
        self.mes_atual = hoje.month
        self.ano_atual = hoje.year
        
        root.title(f"Sistema de Pagamentos - {perfil}")
        root.geometry("1300x750")
        centralizar_janela(root)

        self.vars = {k: tk.StringVar() for k in
                     ["nome", "admissao", "banco", "pix", "salario", "adiant", "va"]}

        self.func_edit = None

        self.payments_repo = PaymentsRepository()
        self.build()
        self.load_table()
        self.aplicar_permissoes()
        self.atualizar_totais()

    # ---------- UI ---------- #

    # ---------- PERÍODO DE PAGAMENTO ----------
    def build(self):    
        periodo = tk.LabelFrame(self.root, text="Período de Pagamento", padx=10, pady=5)
        periodo.pack(fill="x", padx=10, pady=5)

        tk.Label(periodo, text="Mês",).pack(side="left")
        self.ent_mes_pgto = tk.Entry(periodo, width=5)
        self.ent_mes_pgto.pack(side="left", padx=5)

        tk.Label(periodo, text="Ano").pack(side="left")
        self.ent_ano_pgto = tk.Entry(periodo, width=8)
        self.ent_ano_pgto.pack(side="left", padx=5)

        self.ent_mes_pgto.insert(0, str(self.mes_atual))
        self.ent_ano_pgto.insert(0, str(self.ano_atual))

        btn_filtrar = tk.Button(periodo, text="Filtrar", cursor="hand2", command=self.filtrar_periodo)
        btn_filtrar.pack(side="left", padx=15)
        add_hover(btn_filtrar, bg_hover="#a7a7a7")

         # ---- DIAS DE PAGAMENTO ----
        tk.Label(periodo, text="Dia Salário").pack(side="left", padx=(15, 2))
        self.ent_dia_sal = tk.Entry(periodo, width=4)
        self.ent_dia_sal.pack(side="left", padx=5)

        tk.Label(periodo, text="Dia Adiant.").pack(side="left", padx=(10, 2))
        self.ent_dia_adiant = tk.Entry(periodo, width=4)
        self.ent_dia_adiant.pack(side="left", padx=5)

        self.btn_salvar_datas = tk.Button(periodo, text="Salvar Datas", command=self.salvar_datas_pgto)
        self.btn_salvar_datas.pack(side="left", padx=15)
        add_hover(self.btn_salvar_datas, bg_hover="#a7a7a7")

        # ---------- CABEÇALHO COM USUÁRIO E SAIR ----------

        btn_sair = tk.Button(periodo, text="Sair", font=("Segoe UI", 10), **BTN_PADRAO, command=self.logout)
        btn_sair.pack(side="right", padx=10)
        add_hover(btn_sair, bg_hover="#a7a7a7")

        lbl_usuario = tk.Label(periodo,text=f"Usuário: {self.usuario} ({self.perfil})",font=("Segoe UI", 10, "bold"),fg="#333")
        lbl_usuario.pack(side="right", padx=10)
        cor = "#2e7d32" if self.perfil == "MASTER" else "#1565c0"
        lbl_usuario.config(fg=cor)
        lbl_usuario.pack(side="right", padx=10)
    

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

        self.btn_save = tk.Button(actions_form, text="Salvar", font=("Segoe UI", 10), command=self.save, **BTN_VERDE)
        self.btn_save.pack(side="left", padx=5)
        add_hover(self.btn_save, bg_hover="#1d8d4c")

        self.btn_edit = tk.Button(actions_form, text="Editar", font=("Segoe UI", 10), command=self.edit, **BTN_PADRAO)
        self.btn_edit.pack(side="left", padx=5)
        add_hover(self.btn_edit, bg_hover="#a7a7a7")

        self.btn_delete = tk.Button(actions_form, text="Excluir", font=("Segoe UI", 10), command=self.delete, **BTN_VERMELHO)
        self.btn_delete.pack(side="left", padx=5)
        add_hover(self.btn_delete, bg_hover="#c43020")

        cols = ("ID", "Nome", "Banco", "Salário", "VA", "Adiant.", "Total")
        self.tree = ttk.Treeview(self.root, columns=cols, show="headings")

        for c in cols:
            self.tree.heading(c, text=c, command=lambda col=c: self.sort_tree(col, False))
            self.tree.column(c, width=150, anchor="center")
            self.tree.pack(fill="both", expand=True, padx=10, pady=5)

        # ---------- BOTÕES PRINCIPAIS ----------
        btns = tk.Frame(self.root)
        btns.pack(pady=15)

        btn_pix = tk.Button(btns, text="Gerar PIX", font=("Segoe UI", 10), command=self.pix, width=10, **BTN_VERDE)
        btn_pix.pack(side="left", padx=10)
        add_hover(btn_pix, bg_hover="#27ae60")

        btn_pago = tk.Button(btns, text="Marcar Pago", font=("Segoe UI", 10), command=self.mark_paid, **BTN_AZUL)
        btn_pago.pack(side="left", padx=10)
        add_hover(btn_pago, bg_hover="#2980b9")

        btn_rel = tk.Button(btns, text="Relatórios", font=("Segoe UI", 10), command=self.reports, **BTN_ROXO)
        btn_rel.pack(side="left", padx=10)
        add_hover(btn_rel, bg_hover="#8e44ad")

        # ---------- TOTALIZADORES TELA PRINCIPAL ----------
        self.frame_totais = tk.Frame(self.root, bg="#f2f2f2", height=45)
        self.frame_totais.pack(side="bottom", fill="x")
        self.frame_totais.pack_propagate(False)

        self.total_salario_va_var = tk.StringVar(
        value="Total Salário + VA: R$ 0,00"
)
        self.total_adiantamento_var = tk.StringVar(
        value="Total Adiantamento: R$ 0,00"
)
        tk.Label(
            self.frame_totais,
            textvariable=self.total_salario_va_var,
            font=("Segoe UI", 10),
            bg="#f2f2f2"
        ).pack(side="left", padx=20)

        tk.Label(
            self.frame_totais,
            textvariable=self.total_adiantamento_var,
            font=("Segoe UI", 10),
            bg="#f2f2f2"
        ).pack(side="left", padx=40)

    def filtrar_periodo(self):
        mes_txt = self.ent_mes_pgto.get().strip()
        ano_txt = self.ent_ano_pgto.get().strip()

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

    
        # recarrega a tabela principal
        self.load_table()

        messagebox.showinfo(
            "Período aplicado",
            f"Período definido: {mes:02}/{ano}"
        )


    def atualizar_totais(self):
        registros = self._extrair_dados_treeview()

        totais = FinancialService.calcular_totais(registros)

        self.total_salario_va_var.set(
            f"Total Salário + VA: R$ {totais['total_salario_va']:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

        self.total_adiantamento_var.set(
            f"Total Adiantamento: R$ {totais['total_adiantamento']:,.2f}"
            .replace(",", "X").replace(".", ",").replace("X", ".")
        )

            
    def _extrair_dados_treeview(self):
        dados = []
        for item in self.tree.get_children():
            v = self.tree.item(item, "values")
            dados.append({
                "salario": v[3],
                "va": v[4],
                "adiantamento": v[5]
            })
        return dados


    def logout(self):
        if messagebox.askyesno("Sair", "Deseja realmente sair do sistema?"):
            for widget in self.root.winfo_children():
                widget.destroy()

            # delega para quem controla o fluxo
            self.root.event_generate("<<Logout>>")


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
            total = r[3] + r[4] + r[5]
            self.tree.insert("", "end", values=(
                r[0], r[1], r[2], f"{r[3]:.2f}", f"{r[4]:.2f}", f"{r[5]:.2f}", f"{total:.2f}"
            ))
        conn.close()
        self.atualizar_totais()



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
        centralizar_janela(win)

        container = tk.Frame(win, padx=20, pady=20)
        container.pack(fill="both", expand=True)

        tk.Label(container, text=f"Funcionário: {f.nome}", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(0, 10))

        # Nenhuma opção selecionada por padrão
        tipo_pgto = tk.StringVar(value="")

        tk.Label(container, text="Tipo de pagamento:").pack(anchor="w")

        rb_sal = tk.Radiobutton(container, text="Salário + VA", variable=tipo_pgto, value="sal")
        rb_sal.pack(anchor="w", pady=2)

        rb_adi = tk.Radiobutton(container, text="Adiantamento", variable=tipo_pgto, value="adiant")
        rb_adi.pack(anchor="w", pady=2)

        # 🔒 BLOQUEIO POR PAGAMENTO JÁ REALIZADO
        if self._pagamento_ja_realizado(fid, "Salário+VA"):
            rb_sal.config(state="disabled")

        if self._pagamento_ja_realizado(fid, "Adiantamento"):
            rb_adi.config(state="disabled")

        tipo_escolhido = tipo_pgto.get()

        if tipo_escolhido == "sal" and self._pagamento_ja_realizado(fid, "Salário+VA"):
            alert("aviso", "Salário + VA já foi pago neste mês.")
            return

        if tipo_escolhido == "adiant" and self._pagamento_ja_realizado(fid, "Adiantamento"):
            alert("aviso", "Adiantamento já foi pago neste mês.")
            return
        

        def abrir_pix():
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


        tk.Button(container, text="Gerar PIX", command=abrir_pix, **BTN_VERDE).pack(pady=15)

    def mostrar_qr_code(self, payload, nome, valor, descricao):
        win = tk.Toplevel(self.root)
        win.title("PIX Gerado")
        win.geometry("350x450")
        win.resizable(False, False)
        centralizar_janela(win)
        
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
            messagebox.showwarning("Atenção", "Selecione um funcionário")
            return

        fid = self.tree.item(sel)["values"][0]
        f = Funcionario.buscar_por_id(fid)

        win = tk.Toplevel(self.root)
        win.title("Selecionar pagamento")
        win.geometry("300x180")
        win.resizable(False, False)
        win.grab_set()
        centralizar_janela(win)

        mes = datetime.now().month
        ano = datetime.now().year

        salario_pago = self._pagamento_existe(fid, "Salário+VA", mes, ano)
        adiant_pago = self._pagamento_existe(fid, "Adiantamento", mes, ano)
        # - se salário já foi pago → adiantamento vem marcado
        # - salário não pode ser marcado novamente
        var_sal = tk.BooleanVar(value=not salario_pago)
        var_adi = tk.BooleanVar(value=salario_pago and not adiant_pago)


        tk.Label(win, text="O que deseja marcar como pago?").pack(pady=10)

        chk_sal = tk.Checkbutton(win, text="Salário + VA", variable=var_sal)
        chk_sal.pack(anchor="w", padx=20)

        chk_adi = tk.Checkbutton(win, text="Adiantamento", variable=var_adi)
        chk_adi.pack(anchor="w", padx=20)

        if salario_pago:
            chk_sal.config(state="disabled")

        if adiant_pago:
            chk_adi.config(state="disabled")


        def confirmar():
            registrados = []

            if var_sal.get():
                if self._registrar_pagamento(fid, "Salário+VA", f.salario + f.va):
                    registrados.append("Salário+VA")

            if var_adi.get():
                if self._registrar_pagamento(fid, "Adiantamento", f.adiantamento):
                        registrados.append("Adiantamento")
            if not registrados:
                messagebox.showwarning("Nada feito","Nenhum pagamento foi registrado (já existente)."
                        )
            else:
                messagebox.showinfo("Sucesso","Pagamentos registrados: " + ", ".join(registrados)
                        )

            win.destroy()

        frame_btn = tk.Frame(win)
        frame_btn.pack(pady=15)

        tk.Button(frame_btn, text="Confirmar", width=10, command=confirmar)\
            .pack(side="left", padx=5)

        tk.Button(frame_btn, text="Cancelar", width=10, command=win.destroy)\
            .pack(side="left", padx=5)

    def _registrar_pagamento(self, fid, tipo, valor):

        data_pagamento = datetime.now()
        mes = data_pagamento.month
        ano = data_pagamento.year

        conn = get_conn()
        cur = conn.cursor()

        # BLOQUEIO DE DUPLICIDADE
        cur.execute("""
            SELECT 1
            FROM historico_pagamentos
            WHERE funcionario_id = %s
            AND tipo = %s
            AND mes = %s
            AND ano = %s
        """, (fid, tipo, mes, ano))

        if cur.fetchone():
            conn.close()
            return False  # já pago

        # INSERT
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
        return True

    def _pagamento_existe(self, fid, tipo, mes, ano):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT 1
            FROM historico_pagamentos
            WHERE funcionario_id = %s
            AND tipo = %s
            AND mes = %s
            AND ano = %s
            LIMIT 1
        """, (fid, tipo, mes, ano))

        existe = cur.fetchone() is not None
        conn.close()
        return existe
    
   
    def _pagamento_ja_realizado(self, fid, tipo):
        agora = datetime.now()
        mes = agora.month
        ano = agora.year

        conn = get_conn()
        cur = conn.cursor()

        cur.execute("""
            SELECT 1
            FROM historico_pagamentos
            WHERE funcionario_id = %s
            AND tipo = %s
            AND mes = %s
            AND ano = %s
        """, (fid, tipo, mes, ano))

        existe = cur.fetchone() is not None
        conn.close()
        return existe


    # ---------- RELATÓRIOS ---------- #

    def reports(self):
        win = tk.Toplevel(self.root)
        win.title("Relatório Mensal")
        win.geometry("1300x750")
        centralizar_janela(win)

        win.transient(self.root)   # 🔗 Relatório é filho da principal
        win.grab_set()             # 🔒 Bloqueia interação fora
        win.focus_force()          # 🎯 Foco imediato


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
        cols = ("pid", "nome", "salario", "adiant", "total_mes", "ano")
        tree = ttk.Treeview(win, columns=cols, show="headings")

        titulos = ["ID Pgto", "Funcionário", "Salário", "Adiantamento", "Total Mês", "Ano"]

        for c, t in zip(cols, titulos):
            tree.heading(c, text=t)
            tree.column(c, anchor="center", width=180)
            tree.pack(fill="both", expand=True, padx=10, pady=10)

    # ---------- TOTALIZADORES ----------
        lbl_totais = tk.Label(win, text="", font=("Arial", 10, "bold"))
        lbl_totais.pack(pady=5)

        self.dados_cache = []

    # ---------- FILTRAR ----------
        def filtrar():
            tree.delete(*tree.get_children())
            self.dados_cache.clear()

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

            from collections import defaultdict

            pagamentos = defaultdict(lambda: {
                "salario": Decimal("0.00"),
                "adiant": Decimal("0.00")
            })

            # 🔹 AGRUPA POR FUNCIONÁRIO
            for r in rows:
                func_id = r[0]
                nome = r[1]
                tipo = r[2]
                valor = r[3] if r[3] is not None else Decimal("0.00")

                if tipo in ("Salário", "Salário+VA"):
                    pagamentos[(func_id, nome)]["salario"] += valor
                elif tipo == "Adiantamento":
                    pagamentos[(func_id, nome)]["adiant"] += valor

            total_sal = total_adi = total_geral = Decimal("0.00")

            # 🔹 INSERE UMA LINHA POR FUNCIONÁRIO
            for (func_id, nome), valores in pagamentos.items():
                salario = valores["salario"]
                adiant = valores["adiant"]
                total = salario + adiant

                tree.insert("", "end", values=(
                    func_id,
                    nome,
                    format_money(salario),
                    format_money(adiant),
                    format_money(total),
                    ano
                ))

                self.dados_cache.append([func_id, nome, salario, adiant, total])

                total_sal += salario
                total_adi += adiant
                total_geral += total

            lbl_totais.config(
                text=(
                    f"Total Salários: R$ {total_sal:.2f}    "
                    f"Total Adiantamentos: R$ {total_adi:.2f}    "
                    f"Total Geral: R$ {total_geral:.2f}"
                )
    )


    # ---------- EXPORTAR EXCEL ----------
        def exportar_excel():
            if not self.dados_cache:
                messagebox.showwarning("Atenção", "Nenhum dado para exportar")
                return

            caminho = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel", "*.xlsx")]
            )

            if not caminho:
                return

            df = pd.DataFrame(
                self.dados_cache,
                columns=["ID", "Funcionário", "Salário", "Adiantamento", "Total"]
            )
            df.to_excel(caminho, index=False)
            messagebox.showinfo("Sucesso", "Excel gerado com sucesso")

    # ---------- EXPORTAR PDF ----------
        def exportar_pdf():
            if not self.dados_cache:
                messagebox.showwarning("Atenção", "Nenhum dado para exportar")
                return

            caminho = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF", "*.pdf")],
                initialfile="relatorio_pagamentos.pdf"
            )

            if not caminho:
                return

            # Página em paisagem
            c = canvas.Canvas(caminho, pagesize=landscape(A4))
            largura, altura = landscape(A4)

            mes = ent_mes.get().zfill(2)
            ano = ent_ano.get()
            data_geracao = datetime.now().strftime("%d/%m/%Y %H:%M")

            logo_path = resource_path("img/logo_empresa.png")

            def cabecalho():
                # Logo
                if os.path.exists(logo_path):
                    c.drawImage(
                        logo_path,
                        2 * cm,
                        altura - 3.2 * cm,
                        width=4 * cm,
                        preserveAspectRatio=True,
                        mask="auto"
                    )

                # Título
                c.setFont("Helvetica-Bold", 16)
                c.drawCentredString(
                    largura / 2,
                    altura - 2.2 * cm,
                    "RELATÓRIO MENSAL DE PAGAMENTOS"
                )

                c.setFont("Helvetica", 11)
                c.drawCentredString(
                    largura / 2,
                    altura - 3.0 * cm,
                    f"Período: {mes}/{ano}"
                )

                # Linha
                c.setStrokeColor(colors.grey)
                c.line(2 * cm, altura - 3.5 * cm, largura - 2 * cm, altura - 3.5 * cm)

                # Cabeçalho da tabela
                c.setFont("Helvetica-Bold", 10)
                y = altura - 4.3 * cm

                c.drawString(2 * cm, y, "Funcionário")
                c.drawRightString(16 * cm, y, "Salário")
                c.drawRightString(21 * cm, y, "Adiantamento")
                c.drawRightString(26 * cm, y, "Total")

                c.line(2 * cm, y - 4, largura - 2 * cm, y - 4)

                return y - 18

            def rodape():
                c.setFont("Helvetica", 8)
                c.setFillColor(colors.grey)
                c.drawString(
                    2 * cm,
                    1.5 * cm,
                    f"Gerado em: {data_geracao}"
                )
                c.drawRightString(
                    largura - 2 * cm,
                    1.5 * cm,
                    "Sistema de Pagamentos"
                )
                c.setFillColor(colors.black)

            y = cabecalho()
            rodape()

            total_sal = total_adi = total_geral = 0
            c.setFont("Helvetica", 10)

            for d in self.dados_cache:
                if y < 2.5 * cm:
                    c.showPage()
                    y = cabecalho()
                    rodape()
                    c.setFont("Helvetica", 10)

                nome = d[1]
                salario = float(d[2])
                adiant = float(d[3])
                total = float(d[4])

                c.drawString(2 * cm, y, nome[:50])
                c.drawRightString(16 * cm, y, f"R$ {salario:,.2f}")
                c.drawRightString(21 * cm, y, f"R$ {adiant:,.2f}")
                c.drawRightString(26 * cm, y, f"R$ {total:,.2f}")

                total_sal += salario
                total_adi += adiant
                total_geral += total

                y -= 16

            # Totais
            y -= 10
            c.line(2 * cm, y, largura - 2 * cm, y)
            y -= 18

            c.setFont("Helvetica-Bold", 11)
            c.drawString(2 * cm, y, "TOTAIS DO MÊS")
            c.drawRightString(16 * cm, y, f"R$ {total_sal:,.2f}")
            c.drawRightString(21 * cm, y, f"R$ {total_adi:,.2f}")
            c.drawRightString(26 * cm, y, f"R$ {total_geral:,.2f}")

            c.save()
            messagebox.showinfo("Sucesso", "PDF gerado com sucesso")

        
    # ---------- EXCLUIR PAGAMENTO ----------
        def excluir_pagamento():
            if self.perfil != "Master":
                messagebox.showerror(
                    "Permissão negada",
                    "Apenas o Master pode excluir pagamentos."
                )
                return

            sel = tree.selection()
            if not sel:
                messagebox.showwarning("Atenção", "Selecione um pagamento")
                return

            func_id = tree.item(sel)["values"][0]
            nome = tree.item(sel)["values"][1]
            mes = int(ent_mes.get())
            ano = int(ent_ano.get())

            win = tk.Toplevel(self.root)
            win.title("Excluir pagamento")
            win.geometry("330x280")
            win.resizable(False, False)
            win.grab_set()
            centralizar_janela(win)

            # 🔹 CONTAINER PRINCIPAL
            container = tk.Frame(win)
            container.pack(fill="both", expand=True, padx=10, pady=10)

            var_sal = tk.BooleanVar(value=True)
            var_adi = tk.BooleanVar(value=True)

            tk.Label(container, text=f"O que deseja excluir para:\n{nome}?", font=("Segoe UI", 10, "bold")).pack(pady=10)
            chk_sal = tk.Checkbutton(container, text="Salário + VA", variable=var_sal)
            chk_sal.pack(anchor="w", padx=20)

            chk_adi = tk.Checkbutton(container, text="Adiantamento", variable=var_adi)
            chk_adi.pack(anchor="w", padx=20)

            # 🔹 FRAME DOS BOTÕES
            frame_btn = tk.Frame(container)
            frame_btn.pack(fill="x", pady=20)

            def confirmar_exclusao():
                tipos = []

                if var_sal.get():
                    tipos.append("Salário+VA")

                if var_adi.get():
                    tipos.append("Adiantamento")

                if not tipos:
                    messagebox.showwarning(
                        "Atenção",
                        "Selecione ao menos um tipo para excluir."
                    )
                    return

                if not messagebox.askyesno(
                    "Confirmar exclusão",
                    "Tem certeza que deseja excluir:\n\n"
                    + "\n".join(f"- {t}" for t in tipos)
                    + f"\n\nFuncionário: {nome}\nMês/Ano: {mes}/{ano}"
                    ):
                    return

                conn = get_conn()
                cur = conn.cursor()

                for tipo in tipos:
                    cur.execute("""
                        DELETE FROM historico_pagamentos
                        WHERE funcionario_id = %s
                        AND tipo = %s
                        AND mes = %s
                        AND ano = %s
                    """, (func_id, tipo, mes, ano))

                conn.commit()
                conn.close()

                win.destroy()
                filtrar()  # 🔄 recarrega do banco

            messagebox.showinfo(
                "Sucesso",
                "Pagamento(s) excluído(s) com sucesso."
            )

            tk.Button(frame_btn, text="Confirmar", width=12, command=confirmar_exclusao).pack(side="left", expand=True, padx=5)

            tk.Button(frame_btn, text="Cancelar", width=12, command=win.destroy).pack(side="right", expand=True, padx=5)

            # 🔹 FORÇA RECÁLCULO DO LAYOUT
            win.update_idletasks()
            win.minsize(win.winfo_width(), win.winfo_height())


    # ---------- BOTÕES RELATÓRIO ----------
        frame_botoes = tk.Frame(win)
        frame_botoes.pack(pady=10)

        btn_filtrar = tk.Button(frame_botoes, text="Filtrar", font=("Segoe UI", 10), **BTN_PADRAO, command=filtrar)
        btn_filtrar.pack(side="left", padx=5)
        add_hover(btn_filtrar, bg_hover="#a7a7a7")

        btn_export_excel = tk.Button(frame_botoes, text="Exportar Excel", font=("Segoe UI", 10), **BTN_VERDE, command=exportar_excel)
        btn_export_excel.pack(side="left", padx=5)
        add_hover(btn_export_excel, bg_hover="#1d8d4c")

        btn_export_pdf = tk.Button(frame_botoes, text="Exportar PDF", font=("Segoe UI", 10), **BTN_ROXO, command=exportar_pdf)
        btn_export_pdf.pack(side="left", padx=5)
        add_hover(btn_export_pdf, bg_hover="#8e44ad")

        btn_excluir_pagamento = tk.Button(frame_botoes, text="Excluir Pagamento", font=("Segoe UI", 10), **BTN_VERMELHO, command=excluir_pagamento)
        btn_excluir_pagamento.pack(side="left", padx=5)
        add_hover(btn_excluir_pagamento, bg_hover="#c43020")  

        filtrar()