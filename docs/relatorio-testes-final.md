# Relatório de Testes Executados — Conecta Social

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Antonio Pires Felipe — RA 2840482211003
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Luiz Henrique Neres — RA 2840482423005

> Cintia Marcelo de Oliveira (RA 2840482421017) consta do Termo de Aceite do Projeto (E2), mas não participou das Sprints 3 e 4 nem desta bateria final.

**Data da bateria final:** 04/11/2026 (testes automatizados), confirmada no CI do PR #66 em 05/11/2026

**Escopo testado:** as funcionalidades aceitas no Termo de Aceite do Projeto ([`docs/termo-aceite.md`](termo-aceite.md), E2) e todas as histórias entregues do [`docs/backlog.md`](backlog.md) (#1 a #24, sendo 14 Deve ter, 8 Deveria ter e 2 Poderia ter), com os casos de teste CT01 a CT33 do [`docs/plano-de-testes.md`](plano-de-testes.md).

**Estado avaliado:** `main` no commit `d4439ea` (merge do PR #66, em 05/11/2026). Deploy: [https://conecta-social-wcxa.onrender.com/](https://conecta-social-wcxa.onrender.com/).

## 1. Resumo executivo

| Métrica | Valor |
|---|---|
| Total de casos de teste | 33 (CT01 a CT33) |
| Passaram | 33 |
| Falharam | 1 (CT21), corrigido até 05/11/2026 (ver seção 3) |
| Cobertura automatizada (linhas/branches) | 98% em `core` e `conecta`, com 229 testes automatizados ([CI do PR #66](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/42024442513/job/127234998073), PostgreSQL 15) |

A cobertura é medida com o coverage.py (806 instruções, 9 sem cobertura; 164 branches, 8 parciais), sem as migrations, os testes, o `asgi.py` e o `wsgi.py` (configuração em `pyproject.toml`). O CI falha se ela ficar abaixo de 95%.

Nesta bateria, os três casos que ainda estavam pendentes no plano de testes ganharam testes automatizados: CT01 (expiração da sessão) e CT08 (paginação de famílias), que estavam parciais, e CT21 (conteúdo do CSV), que não tinha sido executado. O CT21 falhou na primeira verificação, feita na análise do código e numa execução no shell do Django, porque o CSV não trazia os mesmos dados da tela, como pede a #23. O arquivo foi corrigido e o caso passou.

## 2. Casos de teste — visão consolidada

A coluna "Prioridade" é a do `docs/backlog.md`. A evidência de cada caso, com o nome dos testes, está na seção 4 do `docs/plano-de-testes.md`.

| ID | História | Prioridade | Área | Tipo | Resultado | Observação |
|---|---|---|---|---|---|---|
| CT01 | #1 | Deve ter | Autenticação e Perfis | Integração | Passou | Login válido desde a Sprint 1. A expiração da sessão após 30 minutos sem atividade ganhou teste nesta bateria (`ExpiracaoSessaoTests`, 4 testes) |
| CT02 | #1 | Deve ter | Autenticação e Perfis | Unitário/integração | Passou | Herdado da Sprint 1 |
| CT03 | #3 | Deve ter | Autenticação e Perfis | Unitário/integração | Passou | Herdado da Sprint 1 |
| CT04 | #3 | Deve ter | Autenticação e Perfis | Unitário/integração | Passou | Herdado da Sprint 1 |
| CT05 | #5 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT06 | #5 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT07 | #8 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT08 | #9 | Deve ter | Cadastros Básicos | Integração | Passou | Busca desde a Sprint 2. As colunas da lista e a paginação de 20 por página, com e sem busca, ganharam testes nesta bateria (3 testes em `FamiliaTestCase`) |
| CT09 | #10 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT10 | #11 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT11 | #14 | Deve ter | Movimentações | Integração | Passou | Herdado da Sprint 2; data padrão corrigida no PR #38 |
| CT12 | #16 | Deve ter | Movimentações | Integração | Passou | Herdado da Sprint 2 |
| CT13 | #16 | Deve ter | Movimentações | Integração | Passou | Herdado da Sprint 2 |
| CT14 | #12 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT15 | #20 | Deve ter | Relatórios e Painel | Integração | Passou | Herdado da Sprint 4 (PR #47) |
| CT16 | #21 | Deve ter | Relatórios e Painel | Integração | Passou | Herdado da Sprint 4 (PR #53) |
| CT17 | #21 | Deve ter | Relatórios e Painel | Integração | Passou | Herdado da Sprint 4 (PR #53) |
| CT18 | #2 | Deve ter | Autenticação e Perfis | Integração | Passou | Herdado da Sprint 1 |
| CT19 | #4 | Deveria ter | Autenticação e Perfis | Unitário/integração | Passou | Herdado da Sprint 1 |
| CT20 | #19 | Poderia ter | Movimentações | Unitário/integração | Passou | Entregue em 02/11/2026 (PR #63). O registro do estorno é a própria movimentação marcada como cancelada, com data (`cancelado_em`) e administrador (`cancelado_por`); o registro original não é apagado (ver seção 6) |
| CT21 | #23 | Poderia ter | Relatórios e Painel | Integração | Passou | Falhou na primeira verificação desta bateria (bugs 1 a 3 da seção 3) e passou depois da correção (`ExportarCsvTests`, 7 testes) |
| CT22 | #6 | Deve ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT23 | #7 | Deveria ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT24 | #13 | Deveria ter | Cadastros Básicos | Integração | Passou | Herdado da Sprint 2 |
| CT25 | #15 | Deveria ter | Movimentações | Integração | Passou | Herdado da Sprint 2 |
| CT26 | #17 | Deveria ter | Movimentações | Integração + manual | Passou | Herdado da Sprint 2; a interação em JavaScript foi validada manualmente |
| CT27 | #18 | Deveria ter | Movimentações | Integração | Passou | Herdado da Sprint 2 |
| CT28 | #22 | Deveria ter | Relatórios e Painel | Integração | Passou | Herdado da Sprint 4 (PR #49) |
| CT29 | #14, #16 | Deve ter | Movimentações | Banco (integração) | Passou | Adicionado na Sprint 4 (PR #55) |
| CT30 | #8 | Deve ter | Cadastros Básicos | Banco (integração) | Passou | Adicionado na Sprint 4 (PR #55) |
| CT31 | #3 | Deve ter | Autenticação e Perfis | Banco (integração) | Passou | Adicionado na Sprint 4 (PR #55) |
| CT32 | — (E3) | — | Banco de dados | Banco (integração) | Passou | Migrations iguais ao `db/schema.sql` da E3 (PR #55) |
| CT33 | #24 | Deveria ter | Relatórios e Painel | Integração | Passou | Entregue em 03/11/2026 (PR #64) |

Além dos casos do plano, a suíte tem testes de interface com htmx, segurança em produção (HTTPS, cookies `Secure`, HSTS), desempenho (número de consultas do painel e do relatório) e o comando `seed`. Eles estão listados nas evidências de cada sprint em `docs/sprints/`.

## 3. Bugs encontrados nesta bateria

| # | Descrição | Severidade | Status |
|---|---|---|---|
| 1 | O CSV do relatório de distribuições não neutralizava fórmulas: um nome de família, item ou categoria começando com `=`, `+`, `-` ou `@` virava fórmula ao abrir numa planilha (OWASP, injeção em CSV; lacuna registrada na E8) | Média | Corrigido (PR #66) |
| 2 | O CSV gravava o BOM (marcador de codificação UTF-8) no começo de cada linha, e não só no início do arquivo: nas planilhas, a primeira célula da linha 2 em diante começava com um caractere invisível e a data deixava de ser reconhecida | Média | Corrigido (PR #66) |
| 3 | O CSV não trazia os mesmos dados da tela do relatório, como pede a #23: saía uma linha por distribuição (data, família, item, quantidade e usuário), e não os dados agrupados por família e item da tela | Média | Corrigido (PR #66) |

Critério de severidade: **Alta** = segurança ou perda de dados; **Média** = dado ou regra incorretos, com contorno; **Baixa** = visual ou texto.

## 4. Testes de aceitação com cliente/PO

**Situação em 06/11/2026: pendente.** A sessão de aceitação será feita com o professor da disciplina, que atua como cliente/PO neste tema do banco de temas, presencialmente, em aula, no sistema publicado. Roteiro: [`docs/roteiro-aceitacao.md`](roteiro-aceitacao.md), com um bloco por item do escopo aceito na E2 (cadastro e autenticação de usuários, login, logout, cadastros de categorias, itens e doadores, desativação de usuário, registro de doações, controle de entrada e de saída do estoque e relatórios), mais o cancelamento de movimentação (#19) e o painel do mês (#24). Os testes exploratórios da equipe seguem o checklist da seção 3 do mesmo roteiro (EX01 a EX10). Resultado: será registrado aqui e no [`docs/termo-aceite-cliente.md`](termo-aceite-cliente.md) depois da sessão, com a data e os participantes.

Validação manual já registrada antes desta bateria: CT26 (saldo exibido no formulário de distribuição, interação em JavaScript), na Sprint 2.

## 5. Correções feitas durante o semestre

Defeitos do sistema corrigidos nos PRs e commits `fix:` antes desta bateria. Ficam de fora ajustes de texto, formatação de documentos e remoção de arquivos. As severidades seguem o critério da seção 3.

| PR | Data | Defeito corrigido | Severidade |
|---|---|---|---|
| #30 | 24/09/2026 | Ao editar um doador, a validação de CPF/CNPJ acusava duplicidade com o próprio registro | Média |
| #30 | 24/09/2026 | Faltava a migration do `Item`, então o banco não refletia o model | Média |
| #32 | 24/09/2026 | Telas de cadastro sem o layout com o menu lateral | Baixa |
| #38 | 02/10/2026 | Formulários de doação e distribuição sem a data de hoje como padrão | Baixa |
| #39 | 02/10/2026 | Submenu de movimentações aberto por padrão e sem ícones | Baixa |
| #55 | 30/10/2026 | Colunas e validações do banco diferentes do DDL (`db/schema.sql`) e do DER | Média |
| #58 | 30/10/2026 | Produção sem HTTPS obrigatório, cookies sem `Secure` e erros sem registro | Alta |
| #62 | 02/11/2026 | Página inicial com o andamento desatualizado (sem as Sprints 3 e 4) | Baixa |

## 6. Paridade com o backlog

- **#19, cancelamento (CT20):** o critério "Cancelamento cria um registro de estorno (não apaga o registro original)" é cumprido pela marcação da própria doação ou distribuição como cancelada, com a data e o administrador que cancelou. O registro original continua no banco e aparece no histórico com o selo "Cancelada". A movimentação cancelada sai do saldo, do painel, do relatório e do CSV. Os outros dois critérios ("o saldo é revertido ao valor anterior" e "somente Administrador pode cancelar") têm testes próprios.
- **Sprint da #19 e da #24:** no backlog, a #19 está na Sprint 3 e a #24 não tem sprint. As duas foram entregues depois da Sprint 4: a #19 em 02/11/2026 (PR #63) e a #24 em 03/11/2026 (PR #64).
- **#23, exportação em CSV:** é Poderia ter no backlog, mas consta do item 9 do escopo da E2. Foi entregue e, depois da correção desta bateria, cumpre os dois critérios: o CSV tem os mesmos dados e filtros da tela e o cabeçalho em português.

## 7. Como reproduzir

```bash
coverage run manage.py test
coverage report
```

O CI ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)) roda a mesma suíte no PostgreSQL 15 a cada PR e falha se a cobertura ficar abaixo de 95%. Execução local desta bateria: SQLite, `DEBUG=True`, 04/11/2026. Execução no CI: [job `test` do PR #66](https://github.com/Antonio-pf/projeto-eng-soft/actions/runs/42024442513/job/127234998073) (PostgreSQL 15, `DEBUG=False`), 229 testes OK e 98% de cobertura, em 05/11/2026.
