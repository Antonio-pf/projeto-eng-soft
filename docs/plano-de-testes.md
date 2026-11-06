# Plano de Testes — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

---

## 1. Estratégia

| Tipo de teste | O que cobre | Ferramenta | Quando roda |
|---|---|---|---|
| Unitário | Regra de negócio e validações de domínio (requisitos mínimos do §3): cálculo de saldo, bloqueio por saldo insuficiente, quantidade > 0 e CPF/CNPJ | Django TestCase (unittest) | A cada alteração e a cada PR (CI) |
| Integração | Autenticação e perfis, validações na interface e no banco, relacionamentos e consultas agregadas do relatório e do painel (requisitos mínimos do §3), contra o PostgreSQL | Django TestCase com Client e coverage.py | A cada PR (CI), desde a Sprint 1 |
| Manual/aceitação | Fluxos completos de Administrador e Voluntário no deploy público, com o cliente/PO, e testes exploratórios de usabilidade, mensagens, layout e acessibilidade | Roteiro manual | Ao fim de cada sprint e na bateria final (E9) |

---

## 2. Critério de bloqueio de merge

Nenhum PR é aceito na `main` se:

- (a) Algum teste automatizado existente **quebrar**;
- (b) Uma nova **regra de negócio** (ex.: bloqueio de saldo insuficiente) for adicionada **sem teste unitário correspondente**;
- (c) Falhar qualquer teste crítico de autenticação, autorização, validação, integridade do saldo ou consulta agregada;
- (d) Uma funcionalidade alterar dados sem teste de integração correspondente ou sem preservar as restrições do banco;
- (e) O build, a migração do banco ou a execução da CI falhar;
- (f) O arquivo `requirements.txt` for alterado sem atualização do `README.md`;
- (g) Um model for alterado sem a atualização correspondente do `db/schema.sql` e do dicionário de dados do `docs/der.md` (o CT32 quebra no CI se as colunas divergirem);
- (h) A cobertura dos testes ficar abaixo de 95% (o `coverage report` falha no CI).

---

## 3. Casos de teste planejados (cresce a cada sprint)

> A partir da E5, cada caso implementado precisa de evidência de execução em `docs/sprints/sprint-N-evidencias-teste.md`. O resultado da bateria final está em [`docs/relatorio-testes-final.md`](relatorio-testes-final.md).

| ID   | História (E2) | Cenário                                                                 | Entrada                                                                    | Resultado esperado                                                                                          | Prioridade |
|------|--------------|-------------------------------------------------------------------------|----------------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------|------------|
| CT01 | #1           | Login com credenciais válidas e expiração de sessão                     | e-mail e senha corretos; sessão sem atividade pelo período configurado     | Redireciona para o painel; sessão é criada e expira após inatividade                                         | Alta       |
| CT02 | #1           | Login com credenciais inválidas                                         | senha incorreta                                                            | Exibe mensagem de erro sem revelar qual campo está errado; nenhuma sessão criada                           | Alta       |
| CT03 | #3           | Administrador cadastra Voluntário                                       | nome, e-mail único, senha, perfil=Voluntário                              | Formulário aceita os campos; usuário é salvo; Voluntário não acessa funcionalidades exclusivas de Administrador | Alta       |
| CT04 | #3           | E-mail duplicado no cadastro de usuário                                 | e-mail já existente no banco                                               | Formulário exibe erro de validação sem salvar                                                               | Alta       |
| CT05 | #5           | Cadastro de doador com CPF/CNPJ inválido                                | CPF ou CNPJ em formato inválido                                            | Formulário rejeita com mensagem de erro de formato antes do envio                                           | Alta       |
| CT06 | #5           | CPF/CNPJ duplicado no cadastro de doador                               | CPF ou CNPJ já cadastrado no banco                                         | Formulário exibe erro de validação de unicidade sem salvar                                                 | Alta       |
| CT07 | #8           | Cadastro de família com dados obrigatórios                              | Nome do responsável, endereço, telefone opcional, número de membros=4     | Família salva e aparece imediatamente na lista com os dados informados; número de membros aceita apenas inteiro >= 1 | Alta       |
| CT08 | #9           | Busca e paginação de famílias pelo nome                                  | Texto de busca "Pereira"; mais de 20 registros                           | Lista exibe nome, endereço e membros apenas das famílias encontradas, com no máximo 20 por página         | Alta       |
| CT09 | #10          | Cadastro de categoria de itens                                          | Nome = "Alimentos"                                                         | Categoria salva e disponível para seleção em itens                                                          | Alta       |
| CT10 | #11          | Cadastro de novo item com estoque mínimo                               | Nome, categoria, unidade válida, estoque mínimo = 5                       | Item salvo aparece na lista com saldo zero; unidade pertence à lista permitida e estoque mínimo aceita inteiro >= 0 | Alta       |
| CT11 | #14          | Registro de doação aumenta saldo do item                               | doador, item X com saldo=10, quantidade inteira=5, data padrão             | Após salvar, saldo do item X = 15; doação aparece no histórico do doador e do item                        | Alta       |
| CT12 | #16          | Distribuição com saldo suficiente diminui saldo                         | família, item X com saldo=15, quantidade inteira=5, data padrão            | Após salvar, saldo do item X = 10; distribuição aparece no histórico da família                          | Alta       |
| CT13 | #16          | Distribuição bloqueada por saldo insuficiente                           | item X com saldo=3, quantidade=10                                          | Sistema bloqueia com mensagem "Saldo insuficiente: disponível 3, solicitado 10"; saldo inalterado          | Alta       |
| CT14 | #12          | Itens com saldo ≤ estoque mínimo são destacados na listagem             | item Y com saldo=2 e estoque_minimo=5                                      | Lista exibe nome, categoria, unidade, saldo e estoque mínimo; item Y é destacado visualmente              | Média      |
| CT15 | #20          | Painel agrupa saldo total e reflete movimentações                       | 3 itens na categoria "Alimento", saldos 10, 20, 30; nova movimentação    | Card "Alimento" exibe total = 60 antes e o valor atualizado após a movimentação; alertas aparecem quando aplicável | Média      |
| CT16 | #21          | Relatório de distribuições filtrável por período                        | filtro: data_inicio=01/09/2026, data_fim=30/09/2026                       | Tabela exibe apenas o período filtrado, com família, item, categoria, quantidade total e número de distribuições | Média      |
| CT17 | #21          | Relatório de distribuições filtrável por família                        | filtro: família = "Família Silva"                                         | Tabela exibe apenas a família filtrada, com quantidade total e número de distribuições; filtros podem ser combinados | Média      |
| CT18 | #2           | Logout encerra sessão e bloqueia acesso                                 | usuário logado visualiza e clica em "Sair"                                 | Botão de logout é visível; redireciona para login; tentativa de acessar URL protegida redireciona para login | Média      |
| CT19 | #4           | Usuário desativado não consegue logar                                   | Administrador desativa usuário; esse usuário tenta logar                  | Login recusado; histórico permanece; lista distingue usuários ativos e inativos                          | Baixa      |
| CT20 | #19          | Cancelamento de movimentação reverte saldo                              | Administrador cancela doação de 5 unidades do item X; Voluntário tenta repetir | Administrador reverte o saldo, registro original permanece, estorno é criado; Voluntário não pode cancelar | Baixa      |
| CT21 | #23          | Exportação de relatório em CSV                                          | clicar em "Exportar CSV" com filtros de período e família ativos          | Download de `.csv` com cabeçalho em português e os mesmos dados agregados e filtros exibidos na tela      | Baixa      |
| CT22 | #6           | Listagem, busca e paginação de doadores                                 | nome de busca "Silva"; mais de 20 doadores                               | Lista exibe nome, CPF/CNPJ e data de cadastro; busca filtra por nome e pagina em no máximo 20 registros   | Alta       |
| CT23 | #7           | Edição de doador com CPF/CNPJ duplicado                                 | edição de doador; CPF/CNPJ já usado por outro doador                      | Formulário pré-preenche os dados atuais e rejeita documento já utilizado por outro doador                | Média      |
| CT24 | #13          | Edição de item sem alterar saldo diretamente                             | edição de nome, categoria e unidade; saldo atual conhecido                 | Formulário pré-preenche os dados; dados cadastrais são atualizados e o saldo atual não é editável         | Média      |
| CT25 | #15          | Histórico de doações filtrável por doador e período                     | doador selecionado; intervalo de datas; filtros isolados e combinados      | Lista paginada exibe data, doador, item, quantidade e usuário que registrou, respeitando os filtros        | Média      |
| CT26 | #17          | Exibição do saldo disponível no formulário de distribuição              | seleção do item X; saldo atualizado antes da seleção                     | Formulário exibe o saldo mais recente do item X antes do envio                                             | Média      |
| CT27 | #18          | Histórico de distribuições filtrável por família e período               | família selecionada; intervalo de datas; filtros isolados e combinados     | Lista exibe data, família, item, quantidade e usuário que registrou, respeitando os filtros               | Média      |
| CT28 | #22          | Relatório de doações por doador e item                                  | doações de vários doadores no período                                     | Relatório agrupa por doador e item, exibe os totais e permite filtro por período                          | Média      |
| CT29 | #14, #16      | Banco recusa movimentação com quantidade menor ou igual a zero          | gravação direta, sem formulário, de doação e distribuição com quantidade 0 e -1| O banco rejeita com erro de integridade (`CHECK quantidade > 0`)                                            | Alta       |
| CT30 | #8            | Banco recusa família sem membros                                        | gravação direta de família com `num_membros` = 0                           | O banco rejeita com erro de integridade (`CHECK num_membros >= 1`)                                          | Média      |
| CT31 | #3            | Banco recusa perfil diferente de Administrador e Voluntário             | gravação direta de usuário com perfil `gestor`                             | O banco rejeita com erro de integridade (`CHECK perfil IN (...)`)                                           | Alta       |
| CT32 | — (E3)        | Banco criado pelas migrations igual ao `db/schema.sql`                  | colunas de cada tabela nos models e no `db/schema.sql`                     | As 8 tabelas têm as mesmas colunas, com os mesmos nomes, nos dois                                           | Média      |
| CT33 | #24           | Painel com doações do mês, famílias atendidas e movimentações recentes  | doações e distribuições no mês atual e no anterior, incluindo canceladas   | Cards mostram as doações não canceladas do mês com a variação, as famílias distintas atendidas e as 5 últimas movimentações não canceladas| Média      |
| CT34 | #25           | Aviso de privacidade público, sem login                                 | visitante sem sessão abre `/privacidade/`; `ONG_NOME` e `ONG_CONTATO_PRIVACIDADE` preenchidos e vazios | Página abre sem login e sem consulta ao banco, com as 9 seções: controlador e contato (ou o texto padrão), dados guardados, finalidades com base legal, condição de atendimento, quem acessa, compartilhamento, prazo de 5 anos e direitos; link na tela de login, na página inicial e no rodapé das telas internas | Alta       |
| CT35 | #25           | Aviso nos formulários de novo doador e de nova família                  | formulários abertos na página e no modal; edição de doador pelo Administrador | Os dois formulários de cadastro mostram o aviso com link para o aviso completo em nova aba; o de família destaca que o cadastro é condição para receber doações; a edição de doador não repete o aviso | Média      |
| CT36 | #25           | Anonimização dos cadastros vencidos                                     | doador e família com a última movimentação (cancelada ou não) no limite de 5 anos, um dia depois e sem movimentação; comando rodado duas vezes e com `--simular` | Vencidos ficam como "Titular anonimizado", sem documento, contato e endereço; movimentações e saldo não mudam; quem está no prazo não muda; a segunda execução não anonimiza de novo; `--simular` não grava; listas, históricos, relatório e CSV mostram o titular anonimizado; a edição de doador anonimizado responde 404 | Alta       |
| CT37 | #25           | CPF/CNPJ mascarado na lista de doadores                                 | doador com CPF `123.456.789-01`; perfis Voluntário e Administrador         | A lista mostra `***.***.*89-01` para os dois perfis; a edição do Administrador mostra o número completo  | Média      |
| CT38 | #25           | Aviso de dados pessoais no relatório de distribuições                   | relatório de distribuições aberto por um Voluntário                        | Junto do botão "Exportar CSV", aviso de que o arquivo traz o nome do responsável de cada família         | Baixa      |
| CT40 | #27           | Campos com máscara e validação no servidor                              | letras, pontuação colada, CPF de 11 e CNPJ de 14 dígitos, telefone de 10 e 11 dígitos, quantidade "2,5" e "2.5", telefone de família inválido | Letras são descartadas; CPF/CNPJ e telefone saem formatados; a quantidade com vírgula ou ponto é gravada; telefone de família inválido é recusado com "Informe um telefone válido com DDD."; o saldo aparece com vírgula | Média      |
| CT41 | #28           | Fotos e perfis do GitHub na seção Equipe da página inicial              | visitante abre a página inicial; Antonio e Luiz com foto, Daniel e Alexandre sem foto | Antonio e Luiz aparecem com a foto servida pelo próprio sistema (sem imagem externa); Daniel e Alexandre com as iniciais; os quatro cartões levam ao perfil do GitHub em nova aba e mostram o login | Baixa      |

---

## 4. Situação dos casos de teste

Atualizada a cada sprint a partir das evidências em `docs/sprints/`. Estado em 02/11/2026: **30 passaram, 2 parciais e 1 não executado**. Os testes automatizados rodam com `python manage.py test` (213 testes) e no CI a cada PR, no SQLite e no PostgreSQL.

| ID | História | Situação | Quando | Evidência |
|---|---|---|---|---|
| CT01 | #1 | 🟡 Parcial | Sprint 1 | Login válido: `test_login_valido_redireciona_para_painel`. A expiração da sessão está configurada em `conecta/settings.py`, mas não tem teste automatizado |
| CT02 | #1 | ✅ Passou | Sprint 1 | `AutenticarTests` (senha errada e e-mail inexistente) e `test_login_invalido_mostra_erro_generico_e_nao_autentica` |
| CT03 | #3 | ✅ Passou | Sprint 1 | `UsuarioFormTests` e `UsuariosViewTests` (cadastro, listagem e 403 para Voluntário) |
| CT04 | #3 | ✅ Passou | Sprint 1 | `test_email_duplicado_e_rejeitado` e `test_email_duplicado_mostra_erro_e_nao_duplica` |
| CT05 | #5 | ✅ Passou | Sprint 2 | `DoadorTestCase.test_cpf_formato_invalido` |
| CT06 | #5 | ✅ Passou | Sprint 2 | `DoadorTestCase.test_cpf_duplicado` |
| CT07 | #8 | ✅ Passou | Sprint 2 | `FamiliaTestCase`: cadastro, número de membros inválido e telefone opcional |
| CT08 | #9 | 🟡 Parcial | Sprint 2 | Busca: `test_listar_e_buscar_familias`. A paginação de 20 por página funciona, mas não tem teste automatizado |
| CT09 | #10 | ✅ Passou | Sprint 2 | `CategoriaTestCase` |
| CT10 | #11 | ✅ Passou | Sprint 2 | `test_cadastrar_item_com_sucesso` e `test_cadastrar_item_estoque_minimo_invalido` |
| CT11 | #14 | ✅ Passou | Sprint 2 | `DoacaoTestCase`. A data padrão foi corrigida na Sprint 3 (PR #38) |
| CT12 | #16 | ✅ Passou | Sprint 2 | `test_registrar_distribuicao_com_sucesso` e `test_registrar_distribuicao_saldo_exatamente_igual_permitida` |
| CT13 | #16 | ✅ Passou | Sprint 2 | `test_registrar_distribuicao_saldo_insuficiente_bloqueada` |
| CT14 | #12 | ✅ Passou | Sprint 2 | `test_listar_itens_com_saldo_e_destaque` |
| CT15 | #20 | ✅ Passou | Sprint 4 | `PainelTests.test_ct15_total_da_categoria_soma_os_saldos_e_reflete_movimentacao` (PR #47) |
| CT16 | #21 | ✅ Passou | Sprint 4 | `DistribuicaoRelatorioTestCase.test_ct16_relatorio_distribuicoes_filtra_por_periodo` (PR #53) |
| CT17 | #21 | ✅ Passou | Sprint 4 | `DistribuicaoRelatorioTestCase.test_ct17_relatorio_distribuicoes_filtra_por_familia` (PR #53) |
| CT18 | #2 | ✅ Passou | Sprint 1 | `test_logout_limpa_sessao_e_bloqueia_painel` e `test_painel_sem_sessao_redireciona_para_login` |
| CT19 | #4 | ✅ Passou | Sprint 1 | `test_usuario_inativo_retorna_none` e `test_usuario_desativado_nao_consegue_fazer_login` |
| CT20 | #19 | ✅ Passou | 02/11/2026 | `CancelarMovimentacaoModeloTests.test_ct20_cancelar_doacao_reverte_saldo_e_preserva_registro` e `CancelarMovimentacaoViewTests.test_ct20_voluntario_nao_pode_cancelar`. Saldo negativo, cancelamento repetido, permissões e históricos em `CancelarMovimentacaoModeloTests`, `CancelarMovimentacaoViewTests` e `HistoricoComCanceladasTests` |
| CT21 | #23 | ⬜ Não executado | — | Só o link de exportação tem teste (`test_exportar_csv_leva_os_filtros_do_relatorio`). O conteúdo do CSV não tem teste automatizado nem execução manual registrada |
| CT22 | #6 | ✅ Passou | Sprint 2 | `test_listar_doadores`, `test_buscar_doador_por_nome` e `test_paginacao_doadores` |
| CT23 | #7 | ✅ Passou | Sprint 2 | `DoadorUpdateTestCase` |
| CT24 | #13 | ✅ Passou | Sprint 2 | `ItemTestCase.test_editar_item` |
| CT25 | #15 | ✅ Passou | Sprint 2 | `DoacaoListTestCase`: filtros por doador e período, isolados e combinados |
| CT26 | #17 | ✅ Passou | Sprint 2 | `test_formulario_exibe_saldo_inline_na_opcao_do_item`. A interação em JavaScript foi validada manualmente |
| CT27 | #18 | ✅ Passou | Sprint 2 | `DistribuicaoListTestCase`: filtros por família e período, isolados e combinados |
| CT28 | #22 | ✅ Passou | Sprint 4 | `DoacaoListTestCase`: `test_totais_*` (PR #49) |
| CT29 | #14, #16 | ✅ Passou | 29/10/2026 | `SchemaBancoTests.test_banco_recusa_movimentacao_com_quantidade_menor_ou_igual_a_zero` (PR #55) |
| CT30 | #8 | ✅ Passou | 29/10/2026 | `SchemaBancoTests.test_banco_recusa_familia_sem_membros` (PR #55) |
| CT31 | #3 | ✅ Passou | 29/10/2026 | `SchemaBancoTests.test_banco_recusa_perfil_fora_dos_dois_perfis` (PR #55) |
| CT32 | — (E3) | ✅ Passou | 29/10/2026 | `SchemaBancoTests.test_colunas_das_migrations_iguais_ao_schema_sql` (PR #55) |
| CT33 | #24 | ✅ Passou | 02/11/2026 | `PainelTests.test_ct33_painel_do_mes_conta_doacoes_familias_e_lista_recentes`. Período equivalente do mês anterior, famílias distintas, ordem e limite das movimentações recentes e renderização para os dois perfis nos demais testes de `PainelTests` |
| CT40 | #27 | 🟡 Parcial | 06/11/2026 | `MascarasTests` (atributos dos campos, telefone da família, quantidade com vírgula e ponto, saldo com vírgula, inteiros e script do layout) e roteiro no Chrome e no WebKit, o motor do Safari (25 verificações em cada). Falta o roteiro no Firefox |

Pendências para o Relatório de Testes Executados (E9): CT01 (expiração da sessão), CT08 (paginação de famílias) e CT21 (conteúdo do CSV).

---

## 5. Histórico de versões

| Versão | Data | O que mudou |
|---|---|---|
| 1.1 | 11/09/2026 | Versão inicial da E4: estratégia, critério de bloqueio de merge e casos CT01 a CT28 |
| 1.2 | 29/10/2026 | Situação de cada caso nas Sprints 1 a 4 (seção 4); critério (g) de bloqueio; casos CT29 a CT32, para as validações no banco e o alinhamento com o `db/schema.sql`; caso CT33, para a #24 |
