# Relatório Individual de Contribuição — Sprint 4 — Daniel Souza Monteiro de Carvalho (RA 2840482211052)

**Papel nesta sprint:** [Facilitador / PO / Dados / Qualidade]

> Rascunho com os dados do repositório. Daniel deve revisar, completar e abrir o PR deste arquivo com a própria conta.

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| História #22: totais de doações por doador e item na tela `/doacoes/`, respeitando os filtros de doador e período, com 3 testes (CT28) | `64d3771` — PR #49 (aberto em 25/10/2026) | Concluído, revisado e integrado em 28/10/2026 |
| Implementei a consulta que agrupa as doações por doador e item e soma as quantidades (história #22). | `64d3771` | Integrado no PR #49 |
| Adicionei a seção “Totais por doador e item” ao histórico de doações, com a unidade de medida de cada item. | `64d3771` | Integrado no PR #49 |
| Apliquei os filtros de doador e período aos totais e mantive a exclusão das doações canceladas. | `64d3771` | Integrado no PR #49 |
| Adicionei testes para o histórico e documentei no README como os totais e os filtros funcionam. | `64d3771` | Integrado no PR #49 |

[Declarar aqui se houve uso de IA generativa na história #22]

## 2. Rituais que participei

- [ ] Dailies/weeklies
- [ ] Sprint Review
- [ ] Retrospectiva

[marcar os rituais de que participou, com as datas]

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| [nenhuma revisão registrada no GitHub nesta sprint — completar se houver] | | |

## 4. Dificuldades e o que aprendi

Um desafio foi calcular os totais de todos os registros filtrados, já que o histórico detalhado é paginado. Usei a consulta antes da paginação para agrupar as doações por doador e item e somar as quantidades com o Django.

[Revisar este trecho com as próprias palavras antes da entrega.]
