from db import get_conn


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
        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            SELECT id, nome, admissao, banco, chave_pix,
                   salario_liquido, adiantamento, va, desconto
            FROM funcionarios
            WHERE id = %s
        """, (funcionario_id,))

        row = c.fetchone()
        conn.close()

        if row:
            return Funcionario(
                id=row[0],
                nome=row[1],
                admissao=row[2],
                banco=row[3],
                chave_pix=row[4],
                salario=float(row[5]),
                adiantamento=float(row[6]),
                va=float(row[7]),
                desconto=float(row[8])
            )
        return None

    def salvar(self):
        conn = get_conn()
        c = conn.cursor()

        if self.id:
            c.execute("""
                UPDATE funcionarios
                SET nome=%s, admissao=%s, banco=%s, chave_pix=%s,
                    salario_liquido=%s, adiantamento=%s, va=%s, desconto=%s
                WHERE id=%s
            """, (
                self.nome, self.admissao, self.banco, self.chave_pix,
                self.salario, self.adiantamento, self.va, self.desconto, self.id
            ))
        else:
            c.execute("""
                INSERT INTO funcionarios
                (nome, admissao, banco, chave_pix,
                 salario_liquido, adiantamento, va, desconto)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING id
            """, (
                self.nome, self.admissao, self.banco, self.chave_pix,
                self.salario, self.adiantamento, self.va, self.desconto
            ))
            self.id = c.fetchone()[0]

        conn.commit()
        conn.close()

    def listar():
        conn = get_conn()
        cur = conn.cursor()
        cur.execute("""
            SELECT id, nome, salario_liquido, va, desconto, adiantamento, chave_pix
            FROM funcionarios
            WHERE ativo = TRUE
            ORDER BY nome
        """)
        rows = cur.fetchall()
        conn.close()
        return rows

    def excluir(fid):
        conn = get_conn()
        cur = conn.cursor()
        cur.execute(
            "UPDATE funcionarios SET ativo = FALSE WHERE id = %s",
            (fid,)
        )
        conn.commit()
        conn.close()
