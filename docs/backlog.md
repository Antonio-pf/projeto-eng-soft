# Backlog Priorizado — Conecta Social

**Equipe:** Alexandre Ulhoa, Daniel Carvalho, Cintia Oliveira, Antonio Felipe, Luiz Henrique Neres
**Legenda de prioridade:** Deve ter · Deveria ter · Poderia ter · Não será feito

---

## Autenticação e Perfis

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 1  | Como usuário, quero fazer login com e-mail e senha, para que eu acesse o sistema de forma segura. | - Login com credenciais válidas redireciona para o painel<br>- Credenciais inválidas exibem mensagem de erro sem revelar qual campo está errado<br>- Sessão expira após inatividade | Deve ter | 3 | 1 |
| 2  | Como usuário autenticado, quero fazer logout, para que minha sessão seja encerrada com segurança. | - Botão de logout visível no menu<br>- Após logout, redireciona para a tela de login<br>- Acesso a URL protegida após logout redireciona para login | Deve ter | 1 | 1 |
| 3  | Como Administrador, quero cadastrar novos usuários com perfil Administrador ou Voluntário, para que eu controle quem acessa o sistema e com quais permissões. | - Formulário solicita nome, e-mail, senha e perfil<br>- E-mail duplicado exibe erro de validação<br>- Voluntário recém-criado não acessa funcionalidades exclusivas de Administrador | Deve ter | 3 | 1 |
| 4  | Como Administrador, quero desativar um usuário sem excluí-lo, para que o histórico de ações desse usuário seja preservado. | - Usuário desativado não consegue fazer login<br>- Histórico de movimentações do usuário permanece intacto<br>- Lista de usuários distingue ativos de inativos | Deveria ter | 2 | 1 |

---

## Cadastros Básicos

### Doadores

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 5  | Como Voluntário, quero cadastrar um doador com nome e CPF/CNPJ, para que eu possa vincular doações a uma pessoa identificável. | - Formulário solicita nome (obrigatório), CPF/CNPJ (obrigatório, formato XXX.XXX.XXX-XX), telefone e e-mail (opcionais)<br>- CPF/CNPJ duplicado exibe erro de validação<br>- CPF/CNPJ com formato inválido exibe erro antes de submeter | Deve ter | 3 | 1 |
| 6  | Como Voluntário, quero listar e buscar doadores pelo nome, para que eu encontre rapidamente um doador já cadastrado. | - Lista exibe nome, CPF/CNPJ e data de cadastro<br>- Campo de busca filtra por nome<br>- Lista é paginada (máximo 20 por página) | Deve ter | 2 | 1 |
| 7  | Como Administrador, quero editar os dados de um doador, para que eu corrija informações desatualizadas. | - Formulário de edição pré-preenche os dados atuais<br>- CPF/CNPJ não pode ser alterado para um já usado por outro doador | Deveria ter | 2 | 1 |

### Famílias

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 8  | Como Voluntário, quero cadastrar uma família com nome do responsável e endereço, para que eu possa vincular distribuições a beneficiários identificados. | - Formulário solicita nome do responsável (obrigatório), endereço (obrigatório), telefone (opcional) e número de membros (obrigatório, inteiro ≥ 1)<br>- Família salva aparece imediatamente na lista | Deve ter | 3 | 1 |
| 9  | Como Voluntário, quero listar e buscar famílias pelo nome do responsável, para que eu localize rapidamente a família ao registrar uma distribuição. | - Lista exibe nome do responsável, endereço e número de membros<br>- Campo de busca filtra por nome<br>- Lista é paginada (máximo 20 por página) | Deve ter | 2 | 1 |

### Categorias e Itens

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 10 | Como Administrador, quero cadastrar categorias de itens (ex: Alimento, Roupa, Higiene), para que o estoque fique organizado por tipo. | - Formulário solicita nome da categoria (obrigatório) e descrição (opcional)<br>- Nome duplicado exibe erro de validação | Deve ter | 2 | 1 |
| 11 | Como Administrador, quero cadastrar um item vinculado a uma categoria e com unidade de medida, para que o estoque reflita os tipos reais de doação recebidos. | - Formulário solicita nome (obrigatório), categoria (obrigatório), unidade de medida (obrigatório, selecionada de lista pré-cadastrada: pct, grf, uni, kg, l, m) e estoque mínimo (obrigatório, inteiro ≥ 0)<br>- Item salvo aparece na lista com saldo zero | Deve ter | 3 | 1 |
| 12 | Como Voluntário, quero visualizar a lista de itens com o saldo atual de cada um, para que eu saiba o que está disponível antes de registrar uma distribuição. | - Lista exibe nome, categoria, unidade, saldo atual e estoque mínimo<br>- Itens com saldo ≤ estoque mínimo são destacados visualmente | Deve ter | 2 | 1 |
| 13 | Como Administrador, quero editar os dados de um item, para que eu mantenha o cadastro atualizado sem perder o histórico de movimentações. | - Formulário de edição pré-preenche os dados atuais<br>- O campo de saldo atual não é editável diretamente (apenas movimentações alteram o saldo) | Deveria ter | 2 | 1 |

---

## Movimentações

### Doações (Entrada de Estoque)

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 14 | Como Voluntário, quero registrar uma doação vinculando um doador, um item e uma quantidade, para que o saldo aumente e o histórico fique registrado. | - Formulário solicita doador (seleção), item (seleção), quantidade (inteiro > 0) e data (padrão: hoje)<br>- Após salvar, o saldo do item aumenta exatamente pela quantidade informada<br>- A doação aparece no histórico do doador e do item | Deve ter | 5 | 2 |
| 15 | Como Voluntário, quero visualizar o histórico de doações com filtro por doador e por período, para que eu consulte o que cada doador contribuiu. | - Lista exibe data, doador, item, quantidade e usuário que registrou<br>- Filtros por doador e por intervalo de datas funcionam isolados e combinados<br>- Lista é paginada | Deveria ter | 3 | 2 |

### Distribuições (Saída de Estoque)

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 16 | Como Voluntário, quero registrar uma distribuição vinculando uma família, um item e uma quantidade, para que o saldo diminua e o beneficiário fique registrado. | - Formulário solicita família (seleção), item (seleção), quantidade (inteiro > 0) e data (padrão: hoje)<br>- Se saldo atual < quantidade solicitada, a operação é bloqueada com mensagem de erro ("Saldo insuficiente: disponível X, solicitado Y")<br>- Após salvar com sucesso, o saldo diminui exatamente pela quantidade informada | Deve ter | 5 | 2 |
| 17 | Como Voluntário, quero ver o saldo disponível do item ao preencher o formulário de distribuição, para que eu saiba antes de submeter se a quantidade é viável. | - O saldo atual do item selecionado é exibido no formulário ao selecionar o item<br>- Saldo reflete sempre o valor mais atualizado | Deveria ter | 3 | 2 |
| 18 | Como Voluntário, quero visualizar o histórico de distribuições com filtro por família e por período, para que eu consulte o que cada família recebeu. | - Lista exibe data, família, item, quantidade e usuário que registrou<br>- Filtros por família e por intervalo de datas funcionam isolados e combinados | Deveria ter | 3 | 2 |
| 19 | Como Administrador, quero cancelar uma movimentação registrada por engano, para que o saldo seja corrigido sem apagar o histórico. | - Cancelamento cria um registro de estorno (não apaga o registro original)<br>- O saldo é revertido ao valor anterior<br>- Somente Administrador pode cancelar | Poderia ter | 5 | 3 |

---

## Relatórios e Painel

| #  | História | Critérios de aceite | Prioridade | Pontos | Sprint |
|----|----------|---------------------|------------|--------|--------|
| 20 | Como Voluntário, quero ver um painel com o total de itens em estoque agrupado por categoria, para que eu tenha uma visão geral imediata da situação atual. | - Painel exibe um card por categoria com a soma de saldo de todos os itens da categoria<br>- Itens com saldo ≤ estoque mínimo aparecem numa seção de alertas<br>- Dados refletem as movimentações até o momento do acesso | Deve ter | 5 | 3 |
| 21 | Como Voluntário, quero gerar um relatório de distribuições filtrável por período e por família, para que eu apresente dados de prestação de contas a financiadores. | - Relatório exibe família, item, categoria, quantidade total distribuída e número de distribuições no período<br>- Filtros de data e família funcionam isolados e combinados<br>- Resultado exibido em tabela | Deve ter | 5 | 3 |
| 22 | Como Voluntário, quero ver o histórico de doações por doador com totais por item, para que eu reconheça os maiores contribuidores. | - Relatório agrupa doações por doador, exibindo total de cada item doado<br>- Filtrável por período | Deveria ter | 3 | 3 |
| 23 | Como Voluntário, quero exportar o relatório de distribuições em CSV, para que eu compartilhe os dados com parceiros sem acesso ao sistema. | - Botão "Exportar CSV" gera arquivo com os mesmos dados e filtros aplicados na tela<br>- Arquivo tem cabeçalho com nomes das colunas em português | Poderia ter | 3 | 3 |

---

## Não será feito neste semestre

| # | Funcionalidade | Justificativa |
|---|----------------|---------------|
| F1 | Arrecadação financeira online e links de pagamento | Foco exclusivo em gestão de itens físicos |
| F2 | Gestão contábil (despesas, fluxo de caixa) | Fora do escopo mínimo da disciplina |
| F3 | Aplicativo mobile nativo | Interface web responsiva é suficiente para o MVP |
| F4 | Emissão de Nota Fiscal Eletrônica | Integração com SEFAZ fora do escopo técnico |
| F5 | Integração com APIs de validação (CNPJ, CPF, CEP) | Validação de formato é suficiente para o MVP |
