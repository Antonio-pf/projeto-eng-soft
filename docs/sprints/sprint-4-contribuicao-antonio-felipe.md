# Relatório Individual de Contribuição — Sprint 4 — Antonio Pires Felipe (RA 2840482211003)

**Papel nesta sprint:** Product Owner

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| Integração na `main` dos PRs #46 (correções da E4), #47 (#20, painel) e #49 (#22, de Daniel Carvalho) | merges `410c821`, `ef8b4b7` e `e1417c5` (28/10/2026) | Concluído. #46 e #47 entraram sem revisão de outro integrante |
| Recuperação do deploy: diagnóstico do banco gratuito do Render expirado, troca do banco, execução do `seed` em produção e verificação de `/health/` e do login | painel do Render, 28/10/2026 | Concluído |
| Correções de forma da E2 e da E3: RAs no `db/schema.sql` e título da seção de escopo do termo de aceite | `26603ab` — PR #51 | Concluído, integrado em 29/10/2026 sem revisão de outro integrante |
| História #21 (com Luiz Henrique e Alexandre Ulhoa): alinhamento do relatório de distribuições ao protótipo, com resumo por unidade, link de exportação CSV com os filtros e item no menu lateral; ajuste dos testes de Luiz e 9 testes novos | `d8c463f` — PR #53 | Concluído, integrado em 29/10/2026 sem revisão de outro integrante |
| Simplificação de filtros, formulários e painel, com filtros inválidos nas listas ignorados em vez de gerar erro, e 1 teste novo | `d3285a6` — PR #54 | Concluído, integrado em 29/10/2026 sem revisão de outro integrante |
| Reconciliação do board: #20 em "Done", issue da #19 reaberta e issue #50 criada para a #24 (28/10/2026); issue #22, da história #21, fechada e responsáveis corrigidos para Luiz Henrique e Antonio Felipe (29/10/2026) | board do projeto | Concluído |
| Documentos coletivos da Sprint 3 (E7, com atraso) e da Sprint 4 (E8): relatório, evidências de teste, retrospectiva e rascunhos dos relatórios individuais | `7c89760`, `b44e452` — PR #52 | Integrado em 29/10/2026 sem revisão de outro integrante. Os campos que dependem da equipe (Reviews, retrospectivas e relatórios individuais) ficaram para o fechamento |
| Alinhamento do banco ao DDL e ao DER da E3: migration que renomeia as 10 colunas de chave estrangeira, validações no banco (quantidade > 0, `num_membros >= 1` e perfil), `db/schema.sql` e `docs/der.md` com os tipos reais, 4 testes (CT29 a CT32) e plano de testes na versão 1.2. As migrations foram conferidas em produção depois do deploy | `ae94042`, `e98078f` — PR #55 | Concluído, integrado em 29/10/2026 sem revisão de outro integrante |
| Cadastros e movimentações em modal, listas e históricos filtrando sem recarregar a página, notificação ao salvar e trava contra envio duplicado, com htmx 2.0.11; 53 testes novos (178 no total) | `2ae8ab6` — PR #56 | Concluído, integrado em 30/10/2026 sem revisão de outro integrante |

Uso de IA generativa: a recuperação do deploy, a revisão do protótipo contra o app, o alinhamento da #21 ao protótipo, a simplificação do PR #54, o alinhamento do banco ao DDL (PR #55), os modais com htmx (PR #56) e os rascunhos dos documentos das Sprints 3 e 4 foram feitos com apoio de IA (Claude Code), declarado na descrição dos PRs.

## 2. Rituais que participei

- [x] Dailies/weeklies
- [x] Sprint Review
- [x] Retrospectiva

Encontro online em 23/10/2026 (sexta-feira), com a weekly, a Sprint Review e a retrospectiva da Sprint 4.

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| PR #49 — Totais de doações por doador e item (#22) | Daniel Carvalho | Aprovado em 28/10/2026, antes do merge |

## 4. Dificuldades e o que aprendi

Os merges ficaram concentrados nos últimos dias, quase todos sem revisão. O banco gratuito do Render expirou sem aviso, e o DDL da E3 tinha se afastado do banco real das migrations. Aprendi a conferir o schema real contra o DDL com um teste automatizado e a acompanhar migrations em produção.
