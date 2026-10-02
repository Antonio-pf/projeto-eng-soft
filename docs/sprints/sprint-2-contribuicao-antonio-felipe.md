
# Relatório Individual de Contribuição — Sprint 2 — Antonio Pires Felipe (RA 2840482211003)

**Papel nesta sprint:** Product Owner

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| História #14: registrar doação vinculando doador, item e quantidade, com atualização do saldo | `05ce375` (24/09); integrada à `main` por merge direto em `3c929e3`, sem PR | Concluído |
| Histórias #16 e #17: registrar distribuição com bloqueio por saldo insuficiente e saldo do item exibido no formulário | `2e0f13b` — PR #34 | Concluído |
| Histórias #15 e #18: histórico de doações e de distribuições com filtros por doador/família e período | `0e3e498` — PR #35 | Concluído |
| Telas de cadastro passam a usar o layout com sidebar (`dashboard_base`) | `5adc6bc` — PR #32 | Concluído |
| Ajustes no PR #30 (cadastro de doador): conflito de merge e decorators de autenticação, validação de CPF/CNPJ do próprio registro, migração faltante do Item, CNPJ de teste | `9c78005`, `bf78450`, `18843fa`, `4c57ac3`, `23d1814` | Concluído |
| Correção da data padrão "hoje" nos formulários de doação e distribuição (`DateInput` com `format="%Y-%m-%d"`) e 2 testes de regressão | `core/forms.py`, `core/tests.py` (PR a abrir) | Concluído, falta PR |
| Relatório, evidências de teste e contribuição individual da Sprint 1 (E5) | PR #33 (`8b67146`, `19f0cb3`) | Concluído |
| Reconciliação do board: cards #15 a #18 para "Done", #19 de volta para "Todo", #16 e #17 reatribuídos a mim | board do projeto, 30/09 e 01/10 | Concluído |
| Relatório de entrega, evidências, retrospectiva e GIFs da Sprint 2 (E6) | `docs/sprints/sprint-2-*.md` e `docs/sprints/assets/conecta-social-sprint2-*.gif` | Em andamento |

Uso de IA generativa: as histórias #14 a #18 foram implementadas com apoio substancial de IA
(Claude Code), declarado na descrição dos PRs #34 e #35; consigo explicar o código linha a linha.

## 2. Rituais que participei

- [x] Dailies/weeklies
- [x] Sprint Review (02/10/2026)
- [x] Retrospectiva (02/10/2026)

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| PR #31 — Feature/setup projeto (CRUD de doador, família, categoria e item) | Luiz Henrique Neres | Revisão informal, fora do GitHub: testei a branch localmente antes do merge. Sem aprovação registrada no PR |

Nesta sprint não há nenhuma revisão formal minha registrada no GitHub, e meus PRs #34 e #35
também foram mesclados sem revisão registrada; isso virou ação da retrospectiva.

## 4. Dificuldades e o que aprendi

A maior dificuldade foi manter o board coerente com o repositório: encontrei cards marcados como
"Done" sem código na `main` (#16 a #19) e outros "In Progress" já mesclados (#15 a #18), e só
reconciliei no fim da sprint. Aprendi que o card só deve mudar de coluna depois do merge e que vale
conferir o board contra a `main` antes da aula. Na parte técnica, a regra do saldo (bloquear a
distribuição quando o saldo não cobre a quantidade). Também descobri, ao gravar os GIFs, que a data padrão "hoje" definida no
formulário não aparecia no navegador, porque o `DateInput` usava o formato local e o `type="date"`
exige o formato ISO. Os testes antigos não pegavam isso porque não conferiam o HTML do campo; corrigi
com `format="%Y-%m-%d"` e escrevi um teste de regressão para cada formulário.
