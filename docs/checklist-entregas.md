# Checklist de Entregas — Laboratório de Engenharia de Software

> Fonte: [Modelos de Entregas — LAB·ES](https://ararauna-lab-es-2026-2.netlify.app/modelos_de_entregas_lab_es) (companheiro do Manual do Aluno, ADS Fatec Ribeirão Preto).
> Este documento **não substitui** o site — ele é o mapeamento desse site para o estado real deste repositório, usado como guia de progresso. Antes de dar uma entrega como pronta, releia a entrega correspondente no site (instruções de preenchimento completas + exemplo preenchido do EstágioFatec).

**Projeto:** Conecta Social · **Trilha:** B (Banco de temas nº 4) → **E1b (Declaração de Escopo Compartilhado) não se aplica** (é só para Trilha A).

Legenda: ✅ entregue · 🟡 em andamento/parcial · ⬜ não iniciado

---

## E1 — Semana 1 (21/08)

| # | Documento | Arquivo esperado | Status | Arquivo no repo |
|---|---|---|---|---|
| E1a | Documento de Visão | `docs/documento-de-visao.md` | ✅ | [`docs/documento-de-visao.md`](documento-de-visao.md) |
| E1b | Declaração de Escopo Compartilhado | — | N/A (só Trilha A) | — |

## E2 — Semana 2 (28/08)

| # | Documento | Arquivo esperado | Status | Arquivo no repo |
|---|---|---|---|---|
| E2a | Backlog Priorizado | `docs/backlog.md` | ✅ | [`docs/backlog.md`](backlog.md) |
| E2b | Termo de Aceite do Projeto (assinado pelo professor) | 1 página PDF/Markdown | 🟡 | [`docs/termo-aceite.md`](termo-aceite.md) — falta assinatura do professor (campo em branco no final do arquivo) |

## E3 — Semana 3 (04/09)

| # | Documento | Arquivo esperado | Status | Arquivo no repo |
|---|---|---|---|---|
| E3a | Diagramas UML (casos de uso + classes) | `docs/uml.md` | ✅ | [`docs/uml.md`](uml.md) |
| E3b | DER + dicionário de dados | `docs/der.md` | ✅ | [`docs/der.md`](der.md) |
| E3c | Script DDL | `db/*.sql` | ✅ | [`db/schema.sql`](../db/schema.sql) |

## E4 — Semana 4 (11/09)

| # | Documento | Arquivo esperado | Status | Arquivo no repo |
|---|---|---|---|---|
| E4a | README do Repositório | `README.md` (raiz) | ✅ | [`README.md`](../README.md) |
| E4b | Plano de Testes (versão inicial) | `docs/plano-de-testes.md` | ✅ | [`docs/plano-de-testes.md`](plano-de-testes.md) |
| E4c | Roteiro do Protótipo Navegável | `docs/prototipo.md` + link Figma/Penpot | ✅ | [`docs/prototipo.md`](prototipo.md) |

## E5–E8 — Sprints 1 a 4 (⚠️ ver prazos abaixo)

Cada sprint entrega **4 arquivos**, todos em `docs/sprints/`, sem sobrescrever os das sprints anteriores:

| Sprint | Data | Relatório de Entrega | Ata de Retrospectiva | Contribuição individual (1 por pessoa) | Evidências de Teste |
|---|---|---|---|---|---|
| **E5 (Sprint 1)** | **18/09** ⚠️ amanhã | ⬜ `docs/sprints/sprint-1-relatorio.md` | ⬜ `docs/sprints/sprint-1-retrospectiva.md` | ⬜ `docs/sprints/sprint-1-contribuicao-[nome].md` ×5 | ⬜ `docs/sprints/sprint-1-evidencias-teste.md` |
| E6 (Sprint 2) | 02/10 | ⬜ | ⬜ | ⬜ | ⬜ |
| E7 (Sprint 3) | 16/10 | ⬜ | ⬜ | ⬜ | ⬜ |
| E8 (Sprint 4) | 30/10 | ⬜ | ⬜ | ⬜ | ⬜ |

Nenhum arquivo de sprint existe ainda no repo (`docs/sprints/` não existe). **A Sprint 1 (E5) vence amanhã (18/09)** e nenhuma das 4 peças foi iniciada — ver seção "Próximo passo urgente" abaixo.

Pontos-chave do que cada peça exige (resumo — ver instruções completas no site):
- **Relatório de Entrega**: precisa dos 5 componentes citados no §4 do Manual — incremento funcional demonstrável, backlog atualizado, evidências de teste, ata de retrospectiva e relatório individual — e comparar planejado vs. entregue.
- **Ata de Retrospectiva**: escrita **pela equipe toda em conjunto**, logo após a Sprint Review. Toda ação decidida precisa de responsável, verificável na retrospectiva seguinte.
- **Relatório Individual de Contribuição**: um por integrante (não por equipe), alimenta o fator de contribuição (0,5–1,2) que multiplica a nota do grupo (§6 do Manual). Precisa linkar commits/PRs reais.
- **Evidências de Teste**: atualiza (não substitui) o Plano de Testes da E4b — cada caso de teste com ID (CTxx) precisa de evidência verificável (link do CI, print, nome do arquivo de teste).

## E9 — Semana 13 (06/11)

| # | Documento | Arquivo esperado | Status |
|---|---|---|---|
| E9a | Relatório de Testes Executados (consolidado) | `docs/relatorio-testes-final.md` | ⬜ |
| E9b | Termo de Aceite do Cliente (assinado) | 1 página PDF/Markdown | ⬜ |

## E10 — Semana 14 (13/11, Feira de Projetos)

| # | Documento | Arquivo esperado | Status |
|---|---|---|---|
| E10a | Documentação Final Consolidada | `README.md` atualizado + `docs/documentacao-final.md` | ⬜ |
| E10b | Manual do Usuário (com prints reais de produção) | `docs/manual-do-usuario.md` | ⬜ |
| E10c | Roteiro de Apresentação e Vídeo (3–5 min) | `docs/roteiro-apresentacao.md` + vídeo | ⬜ |

---

## Próximo passo urgente

**Sprint 1 (E5) vence 18/09 e nada foi criado ainda.** Antes de codar mais, a equipe precisa:
1. Ter um incremento funcional demonstrável (algo rodando, não só código) — checar com o time o que já dá pra mostrar.
2. Fazer a Sprint Review + Retrospectiva em conjunto e registrar a ata.
3. Cada um dos 5 integrantes escrever seu relatório individual linkando commits/PRs.
4. Rodar os casos de teste do `docs/plano-de-testes.md` que já foram implementados e registrar evidências.
5. Fechar tudo no Relatório de Entrega da Sprint 1, comparando planejado (backlog E2a) vs. entregue.

## Pendência aberta da E2b

O Termo de Aceite do Projeto (`docs/termo-aceite.md`) ainda tem o campo de assinatura do professor em branco — isso trava formalmente o MVP segundo o §4 do Manual. Vale confirmar com o professor se a assinatura já ocorreu presencialmente ou se falta levar o documento pronto pra aula.

---

*Atualize a coluna Status conforme os arquivos forem criados/mesclados na `main`. Datas conferidas em 17/09/2026 contra o site oficial de modelos — se o site mudar, revise este arquivo.*
