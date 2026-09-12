from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from config.supabase_client import get_supabase


def normalizar_data_admissao(valor):
    valor = (valor or "").strip()
    if not valor:
        return None

    for formato in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(valor, formato).date().isoformat()
        except ValueError:
            continue

    raise ValueError("A admissão deve estar no formato DD/MM/AAAA.")


class Funcionario:
    def __init__(self, id=None, nome="", admissao="", banco="",
                 chave_pix="", salario=0.0, adiantamento=0.0, va=0.0, desconto=0.0):
        self.id = id
        self.nome = nome
        self.admissao = admissao
        self.banco = banco
        self.chave_pix = chave_pix
        self.salario = salario
        self.adiantamento = adiantamento
        self.va = va
        self.desconto = desconto

    @staticmethod
    def buscar_por_id(funcionario_id):
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase não configurado")

        response = (
            supabase
            .table("funcionarios")
            .select("id, nome, admissao, banco, chave_pix, salario_liquido, adiantamento, va, desconto")
            .eq("id", funcionario_id)
            .single()
            .execute()
        )
        row = response.data

        if row:
            return Funcionario(
                id=row["id"],
                nome=row["nome"],
                admissao=row["admissao"] or "",
                banco=row["banco"] or "",
                chave_pix=row["chave_pix"] or "",
                salario=float(row["salario_liquido"] or 0),
                adiantamento=float(row["adiantamento"] or 0),
                va=float(row["va"] or 0),
                desconto=float(row["desconto"] or 0)
            )
        return None

    def salvar(self):
        self.nome = self.nome.strip()
        if not self.nome:
            raise ValueError("Informe o nome do funcionário.")
        for campo in ("salario", "adiantamento", "va", "desconto"):
            try:
                valor = Decimal(str(getattr(self, campo)))
                if not valor.is_finite() or valor < 0:
                    raise ValueError("Valores monetários devem ser finitos e não negativos.")
                valor = valor.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
                if valor > Decimal("9999999999.99"):
                    raise ValueError("Valor acima do limite permitido.")
                setattr(self, campo, float(valor))
            except InvalidOperation as exc:
                raise ValueError("Informe valores monetários válidos.") from exc
        if self.desconto > self.salario + self.va:
            raise ValueError("Desconto não pode ser maior que Salário + VA.")
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase não configurado")

        dados = {
            "nome": self.nome,
            "admissao": normalizar_data_admissao(self.admissao),
            "banco": self.banco,
            "chave_pix": self.chave_pix,
            "salario_liquido": self.salario,
            "adiantamento": self.adiantamento,
            "va": self.va,
            "desconto": self.desconto,
        }
        if self.id:
            (
                supabase
                .table("funcionarios")
                .update(dados)
                .eq("id", self.id)
                .execute()
            )
        else:
            response = (
                supabase
                .table("funcionarios")
                .insert(dados)
                .execute()
            )
            if response.data:
                self.id = response.data[0]["id"]

        return self

    @staticmethod
    def listar():
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase não configurado")

        response = (
            supabase
            .table("funcionarios")
            .select("id, nome, banco, salario_liquido, va, desconto, adiantamento, chave_pix")
            .eq("ativo", True)
            .order("nome")
            .execute()
        )
        return response.data

    @staticmethod
    def excluir(fid):
        supabase = get_supabase()
        if supabase is None:
            raise RuntimeError("Supabase não configurado")

        (
            supabase
            .table("funcionarios")
            .update({"ativo": False})
            .eq("id", fid)
            .execute()
        )
