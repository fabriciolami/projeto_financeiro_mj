import sqlite3


class Funcionario:
    def __init__(self, id=None, nome="", admissao="", banco="",
                 chave_pix="", salario=0.0, adiantamento=0.0, va=0.0):
        self.id = id
        self.nome = nome
        self.admissao = admissao
        self.banco = banco
        self.chave_pix = chave_pix
        self.salario = salario
        self.adiantamento = adiantamento
        self.va = va

    @staticmethod
    def buscar_por_id(funcionario_id):
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()

        c.execute("""
            SELECT id, nome, admissao, banco, chave_pix,
                   salario_liquido, adiantamento, va
            FROM funcionarios
            WHERE id = ?
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
                salario=row[5],
                adiantamento=row[6],
                va=row[7]
            )
        return None

    def salvar(self):
        conn = sqlite3.connect('folha_pagamentos.db')
        c = conn.cursor()

        if self.id:
            c.execute("""
                UPDATE funcionarios
                SET nome=?, admissao=?, banco=?, chave_pix=?,
                    salario_liquido=?, adiantamento=?, va=?
                WHERE id=?
            """, (
                self.nome, self.admissao, self.banco, self.chave_pix,
                self.salario, self.adiantamento, self.va, self.id
            ))
        else:
            c.execute("""
                INSERT INTO funcionarios
                (nome, admissao, banco, chave_pix,
                 salario_liquido, adiantamento, va)
                VALUES (?,?,?,?,?,?,?)
            """, (
                self.nome, self.admissao, self.banco, self.chave_pix,
                self.salario, self.adiantamento, self.va
            ))
            self.id = c.lastrowid

        conn.commit()
        conn.close()
