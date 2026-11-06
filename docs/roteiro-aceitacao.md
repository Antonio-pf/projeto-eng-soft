# Roteiro da Sessão de Aceitação — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Antonio Pires Felipe — RA 2840482211003
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Luiz Henrique Neres — RA 2840482423005

Roteiro impresso da sessão com o cliente (o professor, atuando como cliente) e do checklist de testes exploratórios da E9. Os resultados vão para o [`docs/relatorio-testes-final.md`](relatorio-testes-final.md) (seção 4) e para o [`docs/termo-aceite-cliente.md`](termo-aceite-cliente.md). Cada resultado esperado é o critério de aceite da história no [`docs/backlog.md`](backlog.md).

## 1. Preparação

- [ ] Sistema publicado aberto em [https://conecta-social-wcxa.onrender.com/](https://conecta-social-wcxa.onrender.com/). O serviço está no plano gratuito do Render, que desliga quando fica parado; abra a página alguns minutos antes da sessão para ele já estar no ar.
- [ ] Uma conta de **Administrador** e uma de **Voluntário** prontas. As senhas são entregues pela equipe na hora e não ficam neste documento.
- [ ] Dados de exemplo cadastrados antes da sessão: pelo menos 2 doadores, 2 famílias, 3 itens de categorias diferentes (um deles com saldo abaixo do estoque mínimo), algumas doações e distribuições no mês atual e no anterior.
- [ ] Termo de Aceite do Cliente impresso, e uma planilha (Excel ou LibreOffice) para abrir o CSV.

## 2. Roteiro da sessão

Um bloco por item do escopo aceito na E2b, mais as histórias entregues além dele. Marque **OK?** com S (sim) ou N (não) e anote o que o cliente disser.

### R1. Cadastro e autenticação de usuário voluntário e administrador (#3, Deve ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Como Administrador, abrir **Usuários** e cadastrar um Voluntário | Formulário solicita nome, e-mail, senha e perfil | | |
| Cadastrar outro usuário com o mesmo e-mail | E-mail duplicado exibe erro de validação | | |
| Entrar com o Voluntário recém-criado e tentar abrir **Usuários** pelo endereço | Voluntário recém-criado não acessa funcionalidades exclusivas de Administrador | | |

### R2. Login (#1, Deve ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Entrar com e-mail e senha corretos | Login com credenciais válidas redireciona para o painel | | |
| Entrar com a senha errada | Credenciais inválidas exibem mensagem de erro sem revelar qual campo está errado | | |
| (Demonstrado pela equipe) Explicar a expiração por inatividade de 30 minutos, coberta pelos testes do CT01 | Sessão expira após inatividade | | |

### R3. Logout (#2, Deve ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Localizar **Sair** no menu lateral | Botão de logout visível no menu | | |
| Clicar em **Sair** | Após logout, redireciona para a tela de login | | |
| Colar o endereço do painel no navegador | Acesso a URL protegida após logout redireciona para login | | |

### R4. Cadastro de categorias, itens e doador (#5, #6, #10, #11 Deve ter; #7, #13 Deveria ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| **Itens e categorias** → **Nova categoria**; repetir o mesmo nome | Formulário solicita nome (obrigatório) e descrição (opcional); nome duplicado exibe erro de validação (#10) | | |
| **Novo item** com unidade e estoque mínimo | Formulário solicita nome, categoria, unidade de medida da lista (pct, grf, uni, kg, l, m) e estoque mínimo inteiro ≥ 0; item salvo aparece na lista com saldo zero (#11) | | |
| Editar o item | Formulário pré-preenche os dados atuais; o saldo atual não é editável diretamente (#13) | | |
| **Doadores** → **Novo doador** com CPF inválido e depois com CPF já usado | CPF/CNPJ com formato inválido exibe erro antes de submeter; CPF/CNPJ duplicado exibe erro de validação (#5) | | |
| Buscar o doador pelo nome | Lista exibe nome, CPF/CNPJ e data de cadastro; busca filtra por nome; lista paginada com no máximo 20 por página (#6) | | |
| Editar o doador e tentar usar o CPF/CNPJ de outro | Formulário pré-preenche os dados atuais; CPF/CNPJ não pode ser alterado para um já usado (#7) | | |

### R5. Desativação de usuário sem exclusão (#4, Deveria ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Em **Usuários**, desativar o Voluntário criado no R1 | Lista de usuários distingue ativos de inativos | | |
| Tentar entrar com o usuário desativado | Usuário desativado não consegue fazer login | | |
| Abrir o histórico de doações | Histórico de movimentações do usuário permanece intacto | | |

### R6. Registro das doações realizadas (#14 Deve ter; #15 Deveria ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| **Movimentações** → **Nova doação** | Formulário solicita doador, item, quantidade (inteiro > 0) e data (padrão: hoje) (#14) | | |
| Salvar e conferir o item em **Itens e categorias** | O saldo do item aumenta exatamente pela quantidade informada; a doação aparece no histórico (#14) | | |
| **Histórico de doações** com filtro por doador e por período | Lista exibe data, doador, item, quantidade e usuário que registrou; filtros isolados e combinados; lista paginada (#15) | | |

### R7. Controle de entrada de doações no estoque (#12, Deve ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Abrir **Itens e categorias** | Lista exibe nome, categoria, unidade, saldo atual e estoque mínimo | | |
| Localizar o item com saldo abaixo do mínimo | Itens com saldo ≤ estoque mínimo são destacados visualmente | | |

### R8. Controle de saída de doações para as famílias (#8, #9, #16 Deve ter; #17, #18 Deveria ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| **Famílias** → **Nova família** | Formulário solicita nome do responsável, endereço, telefone (opcional) e número de membros (inteiro ≥ 1); a família salva aparece imediatamente na lista (#8) | | |
| Buscar a família pelo nome | Lista exibe nome do responsável, endereço e número de membros; busca filtra por nome; lista paginada com no máximo 20 por página (#9) | | |
| **Nova distribuição**: escolher o item | O saldo atual do item selecionado é exibido no formulário (#17) | | |
| Pedir mais do que o saldo | A operação é bloqueada com a mensagem "Saldo insuficiente: disponível X, solicitado Y" (#16) | | |
| Registrar uma quantidade válida | O saldo diminui exatamente pela quantidade informada (#16) | | |
| **Histórico de distribuições** com filtro por família e por período | Lista exibe data, família, item, quantidade e usuário que registrou; filtros isolados e combinados (#18) | | |

### R9. Relatório para prestação de contas (#20, #21 Deve ter; #22 Deveria ter; #23 Poderia ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Abrir o **Painel** | Um card por categoria com a soma de saldo dos itens; itens com saldo ≤ estoque mínimo numa seção de alertas; dados refletem as movimentações até o acesso (#20) | | |
| **Relatório de distribuições** com filtro de período e de família | Exibe família, item, categoria, quantidade total distribuída e número de distribuições; filtros isolados e combinados; resultado em tabela (#21) | | |
| **Histórico de doações**, totais por doador | Agrupa doações por doador, com o total de cada item; filtrável por período (#22) | | |
| No relatório filtrado, clicar em **Exportar CSV** e abrir na planilha | O arquivo tem os mesmos dados e filtros da tela e o cabeçalho com nomes das colunas em português (#23) | | |

### R10. Entregue além do escopo da E2b (#19 Poderia ter; #24 Deveria ter)

| Passo | Resultado esperado (critério do backlog) | OK? | Observação do cliente |
|---|---|---|---|
| Como Administrador, no **Histórico de doações**, clicar em **Cancelar** numa doação e confirmar | O registro original não é apagado: aparece com o selo "Cancelada", com data e administrador (o registro do estorno); o saldo é revertido ao valor anterior (#19) | | |
| Entrar como Voluntário e procurar o botão **Cancelar** | Somente Administrador pode cancelar (#19) | | |
| Voltar ao **Painel** | Card "Doações recebidas" com as doações não canceladas do mês e a variação; card "Famílias atendidas" com as famílias distintas do mês; "Movimentações recentes" com as 5 últimas não canceladas, com tipo, doador ou família e quantidade (#24) | | |

## 3. Checklist de testes exploratórios

Executado pela equipe no sistema publicado, antes ou depois da sessão. Os resultados vão para a seção 4 do relatório de testes; um problema encontrado vira uma linha na seção 3 (bugs).

| ID | Perfil | O que verificar | Resultado | Problema encontrado |
|---|---|---|---|---|
| EX01 | Voluntário | Abrir pelo endereço as telas exclusivas do Administrador (Usuários, nova categoria, novo item, editar doador, cancelar movimentação) | | |
| EX02 | Ambos | Enviar formulários vazios ou com dados inválidos: as mensagens dizem o que corrigir, em português, perto do campo | | |
| EX03 | Voluntário | Distribuir mais do que o saldo, e exatamente o saldo | | |
| EX04 | Ambos | Usar no celular: menu, modais, tabelas e botões | | |
| EX05 | Ambos | Deixar a sessão parada por mais de 30 minutos e clicar num filtro ou abrir um modal: volta para o login | | |
| EX06 | Ambos | Abrir o CSV numa planilha: acentos corretos, uma linha por família e item, a coluna "Último registro" reconhecida como data. Cadastrar uma família com nome começando com `=` e conferir que a célula não vira fórmula | | |
| EX07 | Administrador | Cancelar uma doação que deixaria o saldo negativo (deve ser bloqueado) e cancelar duas vezes a mesma movimentação | | |
| EX08 | Ambos | Registrar uma doação e uma distribuição e conferir o painel sem recarregar a página | | |
| EX09 | Ambos | Navegar só pelo teclado (Tab, Enter, Esc nos modais) | | |
| EX10 | Ambos | Situações inesperadas: duplo clique em "Registrar", voltar do navegador depois de salvar, filtros sem resultado, página que não existe | | |

## 4. Depois da sessão

- [ ] Passar o resultado da sessão e do checklist para a seção 4 do relatório de testes.
- [ ] Preencher o termo do cliente (observações, ressalvas confirmadas, parecer, nomes e RAs de quem acompanhou).
- [ ] Anexar o PDF assinado pelo cliente (ou o e-mail de confirmação) e citar a data no termo.
