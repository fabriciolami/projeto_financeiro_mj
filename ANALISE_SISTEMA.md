# Análise do sistema de pagamentos

Data: 11/09/2026.

## Resultado

O projeto tem uma base utilizável para um trabalho acadêmico: interface Tkinter,
autenticação Supabase, cadastro de funcionários, geração de QR Code PIX,
registro manual de pagamentos e exportações. A revisão local encontrou e corrigiu
defeitos concretos, mas não certifica o funcionamento completo no ambiente real.
Não foram usados usuários reais, executadas transferências ou alterados dados no banco.

## Correções realizadas

- Removidos marcadores de conflito de Git do requirements.txt e declarada a dependência requests.
- Normalizado o perfil MASTER, corrigindo os bloqueios indevidos para marcar e excluir pagamentos.
- Relatórios e exclusões passaram da conexão PostgreSQL direta para a API Supabase autenticada.
- Relatórios consideram somente registros CONFIRMADOS e identificam corretamente o ID do funcionário.
- A ação manual Marcar Pago grava CONFIRMADO, com autor e data da confirmação.
  Essa ação continua restrita ao MASTER, preservando a regra da interface original.
- Mensagem de exclusão bem-sucedida passou a aparecer depois da operação.
- Logout chama sign_out; o evento Enter do login é removido após autenticação.
- A janela principal volta a permitir redimensionamento após o login.
- Recursos gráficos são localizados a partir da pasta do projeto.
- Cadastro rejeita nome vazio, números negativos, NaN, infinito, valores acima
  da capacidade das colunas e desconto superior ao salário mais VA.
- Totalizadores usam Decimal e o PIX usa o período aplicado no filtro.
- Falha ao carregar a tela principal mostra uma mensagem e retorna ao login.

## Verificações executadas

- `python -m unittest discover -s tests -v`: oito testes aprovados.
- Sintaxe dos 24 arquivos Python: aprovada.
- Importação de main e dependências da aplicação: aprovada.
- Leitura das declarações de requirements com packaging: aprovada.
- `git diff --check`: aprovado.
- `python -m pip check`: identificou conflito entre fastapi 0.115.0 e starlette
  1.3.1 no ambiente existente. FastAPI não faz parte deste aplicativo;
  o ambiente não foi alterado. Uma instalação limpa das versões declaradas não foi testada.

Os testes simulam o cliente Supabase. Eles verificam datas, validação monetária,
precisão dos totais, permissões locais, vetor conhecido do CRC, gravação da
confirmação manual, bloqueio sequencial de duplicatas e filtro do relatório.
Não comprovam políticas RLS reais, concorrência, compatibilidade bancária do PIX
ou aparência da interface.

## Pendências relevantes

1. **Fluxo de aprovação incompleto.** O SQL prevê MASTER, FINANCEIRO e CONFIRMADOR,
   mas não há telas para registrar pendências e depois confirmá-las por outro usuário.
   O caminho funcional revisado é a confirmação manual pelo MASTER. Definir com os
   requisitos acadêmicos se haverá aprovação em duas etapas.
2. **Histórico antigo.** Registros PENDENTES ou CANCELADOS continuam ocupando a
   combinação funcionário/tipo/mês/ano e bloqueiam novos lançamentos. Não foram
   convertidos automaticamente: é preciso verificar a situação de cada registro.
   Agora somente CONFIRMADOS entram no relatório.
3. **RLS precisa de reforço.** No SQL fornecido, a política de INSERT no histórico
   permite FINANCEIRO inserir status CONFIRMADO com os demais campos preenchidos.
   A política de UPDATE do CONFIRMADOR não restringe alterações de valor, funcionário
   e período. As permissões da interface não substituem restrições no servidor.
   Usuários autenticados sem perfil também podem consultar tabelas com `using (true)`.
4. **SQL e ambiente remoto.** Não foi comparado o schema fornecido com o banco ativo.
   Reexecutar o arquivo inteiro pode falhar porque as políticas já existentes não
   usam uma estratégia de migração. Não executar indiscriminadamente sobre o banco.
5. **PIX.** A geração de QR Code não executa nem confirma uma transferência bancária.
   O gerador ainda precisa de validação com especificação e aplicativo bancário:
   nomes acentuados, tamanho e caracteres do txid, chave inválida e ambiguidade entre
   CPF e telefone de 11 dígitos. O teste do CRC cobre apenas um vetor ASCII.
6. **Interface e falhas de rede.** Há consultas síncronas na thread Tkinter e ações
   sem tratamento específico de erro. Indisponibilidade pode congelar temporariamente
   a tela ou interromper callbacks. Dois pagamentos selecionados são inseridos
   separadamente; pode haver sucesso parcial. Concorrência pode disparar erro de
   unicidade após a consulta inicial de duplicidade.
7. **Entrada monetária.** O formulário aceita `1234,56` ou `1234.56`, mas ainda não
   aceita `1.234,56`. Alguns cálculos individuais e exportações continuam usando float.
8. **Relatórios.** Paginação da API, exportações com muitos registros, nomes longos e
   mudanças de período depois de filtrar precisam de teste. As consultas não implementam
   paginação explícita e podem receber somente o limite configurado no servidor.
9. **Atualizador.** Compara versões como texto e manipula parte da interface em thread
   secundária. O fluxo do executável não foi executado nem validado.
10. **Configuração.** Há configuração MySQL antiga sem uso e conexão PostgreSQL direta
    em db.py que deixou de ser usada pela interface. A tabela pagamentos não é usada
    pelo fluxo revisado. A configuração local tem prioridade sobre variáveis de ambiente;
    não há carregamento explícito de `.env`. Usar chave pública do projeto no aplicativo,
    com RLS; não distribuir chave administrativa. Valores locais não foram exibidos.

## Roteiro de validação antes da entrega

Usar projeto Supabase de testes e contas próprias para cada perfil.

1. Verificar tabelas, relacionamentos, linha configs de ID 1 e perfil associado a cada usuário.
2. Entrar com login válido, inválido e usuário sem perfil; testar logout e novo login.
3. Cadastrar funcionário fictício, editar, desativar e conferir preservação do histórico.
4. Conferir salário 2000, VA 300, desconto 100 e adiantamento 500:
   salário mais VA líquido 2200, adiantamento 500, total exibido 2700.
   Confirmar se a regra acadêmica exige descontar o adiantamento do salário;
   o código atual trata os valores como parcelas independentes.
5. Aplicar período, gerar PIX e conferir destinatário e valor sem concluir pagamento real.
6. Marcar pagamento com MASTER e conferir status, autores, data e bloqueio de duplicidade.
7. Conferir relatório e exportações Excel/PDF com registros fictícios, incluindo várias páginas.
8. Testar exclusão em dados fictícios, cancelamento da janela e seleção múltipla.
9. Testar as restrições diretamente pela API com cada perfil, além dos botões da tela.
10. Simular conexão indisponível e validar instalação em ambiente virtual limpo.

As questões da faculdade podem orientar a implementação do fluxo de aprovação,
documentação de requisitos, diagramas e critérios de aceite.
