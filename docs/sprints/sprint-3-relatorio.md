# Relatório de Entrega — Sprint 3 — Conecta Social

**Período:** 03/10/2026 a 16/10/2026 (Sprint 3, semanas 9–10)
**Sprint Review:** 16/10/2026, encontro online. Participantes: Alexandre Ulhoa, Daniel Carvalho, Antonio Felipe e Luiz Henrique

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

> Este relatório foi escrito em 28/10/2026, depois do prazo da E7 (16/10/2026). Ele descreve o
> estado da `main` no último commit antes do prazo, `76acbde` (09/10/2026, merge do PR #48), e
> registra à parte o que só foi integrado depois.

## 1. Planejado vs. entregue

| História (E2) | Planejada para esta sprint? | Entregue? | Observação |
|---|---|---|---|
| #19 — Cancelar uma movimentação registrada por engano | Sim | Não | Não foi iniciada. O model já tem o campo `cancelado`, mas não existe view nem rota de cancelamento. A issue estava fechada com o card em "Todo"; foi reaberta em 28/10/2026 |
| #20 — Painel com total de itens em estoque por categoria | Sim | Não (fora do prazo) | Implementada no PR #47, aberto em 09/10/2026, mas integrada à `main` só em 28/10/2026 e sem revisão registrada. Entra como incremento da Sprint 4 |
| #21 — Relatório de distribuições filtrável por período e família | Sim | Parcial | Os filtros por família e período e a exportação existem na tela de histórico (`/distribuicoes/`, história #18). Falta a tabela agregada pedida no critério de aceite (família, item, categoria, quantidade total e número de distribuições), que é a tela `2603:727` do protótipo |
| #22 — Histórico de doações por doador com totais por item | Sim | Não (fora do prazo) | Implementada no PR #49 (Daniel Souza), aberto em 25/10/2026 e integrado em 28/10/2026 com revisão. Entra como incremento da Sprint 4 |
| #23 — Exportar o relatório de distribuições em CSV | Sim | Sim, sem teste | O código está na `main` desde 02/10/2026 (commit direto `12ecff3`, sem PR). Não há teste automatizado da exportação (CT21) |
| Página inicial de apresentação do projeto | Não (fora do backlog) | Sim | PR #42. Página pública em `/`, com seções do projeto e da equipe e atalho de login |
| Remoção dos artefatos do AI-DLC do repositório | Não (manutenção) | Sim | PR #48 |

Resultado da sprint: das 5 histórias planejadas, 1 entrou na `main` no prazo (#23, sem teste), 1 ficou parcial (#21) e 3 não entraram (#19, #20 e #22). As histórias #20 e #22 ficaram prontas depois do prazo.

## 2. Incremento funcional demonstrável

O incremento que estava na `main` em 16/10/2026 é pequeno: a página inicial pública (PR #42) e a exportação de distribuições em CSV (#23), que já existia desde o fim da Sprint 2.

- **Página inicial:** `/` mostra a apresentação do projeto e da equipe. O visitante vê o botão **Entrar**; o usuário logado vê o atalho para o painel.
- **Exportar CSV (#23):** em `/distribuicoes/`, o botão de exportação gera `relatorio_distribuicoes.csv` com os mesmos filtros da tela (família e período), sem as distribuições canceladas.

**Deploy:** https://conecta-social-wcxa.onrender.com/. Ninguém verificou o deploy em 16/10/2026. Em 28/10/2026 ele estava fora do ar porque o banco PostgreSQL gratuito do Render expirou e foi apagado (`failed to resolve host`). Um banco novo foi criado, o `seed` foi executado e o deploy voltou em 28/10/2026: `/health/` responde 200 e o login com `admin@conectasocial.org` redireciona para `/painel/`.

**Como reproduzir localmente o estado do prazo** (passo a passo completo no [`README.md`](../../README.md)):

```bash
git checkout 76acbde
source .venv/bin/activate
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Telas desta sprint: `/` (página inicial) e `/distribuicoes/` (botão de exportação CSV).

## 3. Backlog atualizado

Link do board: https://github.com/users/Antonio-pf/projects/11

[Print do board ao fim da Sprint 3 — não foi capturado em 16/10/2026; anexar se existir]

Situação das histórias da Sprint 3 no board, conferida em 28/10/2026:

- **Done:** #23 (exportar CSV). #20 e #22 também estão em "Done", mas só depois do merge de 28/10/2026, já na Sprint 4.
- **In Progress:** #21 (relatório de distribuições). A issue segue aberta.
- **Todo:** #19 (cancelar movimentação). A issue estava fechada sem código na `main` e foi reaberta em 28/10/2026.
- **Novo card:** #24 (cards de doações, famílias atendidas e movimentações recentes no painel) estava no backlog sem card; ganhou a issue #50 e entrou no board em "Todo" em 28/10/2026.

## 4. Evidências de teste

90 testes automatizados (`python manage.py test`), 100% passando no commit `76acbde`, executados em 28/10/2026. São 13 testes novos em relação ao fim da Sprint 2, todos de layout, navegação, data padrão nos formulários e página inicial. O CI (GitHub Actions, jobs `lint` e `test`) passou em todos os merges da `main` desta sprint.

Os casos de teste das histórias da sprint não foram executados: CT15 (#20), CT16 e CT17 (#21), CT20 (#19), CT21 (#23) e CT28 (#22).
Detalhe completo em [`sprint-3-evidencias-teste.md`](sprint-3-evidencias-teste.md).

## 5. Retrospectiva e contribuição individual

- Ata de retrospectiva: [`docs/sprints/sprint-3-retrospectiva.md`](sprint-3-retrospectiva.md)
- Relatórios individuais de contribuição:
  - [Alexandre Ulhoa](sprint-3-contribuicao-alexandre-ulhoa.md)
  - [Daniel Carvalho](sprint-3-contribuicao-daniel-carvalho.md)
  - [Antonio Felipe](sprint-3-contribuicao-antonio-felipe.md)
  - [Luiz Henrique](sprint-3-contribuicao-luiz-henrique.md)

## 6. Riscos/impedimentos para a próxima sprint

- **Sprint 4 acumulada:** chega com #19 e #21 abertas, além das entregas atrasadas desta sprint. O prazo da E8 é 30/10/2026.
- **#21 é "Deve ter":** sem a tabela agregada, uma história Must fica aberta no fim do MVP.
- **Merge semanal:** a `main` ficou sem merge de 09/10 a 28/10/2026, e o PR #47 (#20) esperou 19 dias por revisão.
- **Revisão de PR:** dos PRs integrados nesta sprint, só #43 e #45 tiveram revisão registrada no GitHub. #42, #44 e #48 entraram sem revisão.
- **Deploy:** o banco novo do Render também é gratuito e expira em 30 dias, por volta de 27/11/2026, depois da apresentação final (13/11/2026).
- **Testes de integração:** a exportação CSV (#23) segue sem teste automatizado, e CT01 (expiração de sessão) e CT08 (paginação de famílias) continuam pendentes desde a Sprint 2.
