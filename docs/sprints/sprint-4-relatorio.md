# Relatório de Entrega — Sprint 4 — Conecta Social

**Período:** 17/10/2026 a 30/10/2026 (Sprint 4, semanas 11–12)
**Sprint Review:** [data e participantes da Review da Sprint 4 — confirmar com a equipe]

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

> Rascunho escrito em 28/10/2026 e atualizado em 29/10/2026, com a `main` no commit `58ef94a` (merges dos PRs #54, #53 e #51).

## 1. Planejado vs. entregue

O backlog não registra um planejamento próprio da Sprint 4. A sprint ficou com as histórias que sobraram da Sprint 3 (#19 a #22) e com a #24, que estava sem sprint. [confirmar com a equipe o que foi planejado]

| História (E2) | Planejada para esta sprint? | Entregue? | Observação |
|---|---|---|---|
| #20 — Painel com total de itens em estoque por categoria | Sim (remanescente da Sprint 3) | Sim | PR #47, integrado em 28/10/2026 sem revisão registrada. Mostra os indicadores "Itens em estoque" e "Itens em alerta", o estoque por categoria com o percentual de itens acima do mínimo e os pontos de atenção (até 5 itens de menor saldo), seguindo o frame `2603:39` do protótipo |
| #22 — Histórico de doações por doador com totais por item | Sim (remanescente da Sprint 3) | Sim | PR #49 (Daniel Souza), revisado e aprovado por Antonio Felipe e integrado em 28/10/2026. A tela `/doacoes/` ganhou a tabela "Totais por doador e item", que respeita os filtros de doador e período e exclui as doações canceladas |
| #21 — Relatório de distribuições filtrável por período e família | Sim (remanescente da Sprint 3) | Sim | PR #53, integrado em 29/10/2026 sem revisão registrada. Luiz Henrique refez a implementação a partir da `main` atual, sem a pasta `venv/` (commit `56ce3c6`): rota `/distribuicoes/relatorio/`, agrupamento por família e item, filtros por período e família e 5 testes. Antonio Felipe alinhou a tela ao protótipo, com o resumo por unidade, o link de exportação CSV com os filtros aplicados e o item no menu lateral, ajustou esses testes e acrescentou mais 9 (commit `d8c463f`) |
| #19 — Cancelar uma movimentação registrada por engano | Sim (remanescente da Sprint 3) | Não | Não iniciada. Issue reaberta e card em "Todo" desde 28/10/2026 |
| #24 — Painel com doações recebidas, famílias atendidas e movimentações recentes | [confirmar] | Não | Ganhou a issue #50 e entrou no board em "Todo" em 28/10/2026 |
| Correções da E4 pedidas pelo professor (README no setup nativo e link único do protótipo) | Sim | Sim | PR #46, integrado em 28/10/2026 sem revisão registrada |
| Correções de forma da E2 e da E3 (título da seção de escopo no termo de aceite e RAs no DDL) | Não | Sim | PR #51 (Antonio Felipe), integrado em 29/10/2026 sem revisão registrada |
| Simplificação de filtros, formulários e painel, com filtros inválidos nas listas ignorados em vez de gerar erro | Não | Sim | PR #54 (Antonio Felipe), integrado em 29/10/2026 sem revisão registrada, com 1 teste novo |
| Documentos da Sprint 3 (E7), entregues com atraso | Não | Em andamento | Branch `docs/sprint-3` |

## 2. Incremento funcional demonstrável

O sistema está no ar em https://conecta-social-wcxa.onrender.com/. Em 28/10/2026 o deploy estava fora do ar porque o banco PostgreSQL gratuito do Render expirou. Um banco novo foi criado, as migrations rodaram no deploy e o `seed` foi executado. Depois disso, `/health/` respondeu 200, o login com `admin@conectasocial.org` redirecionou para `/painel/` e as telas `/painel/`, `/itens/` e `/distribuicoes/` abriram com os dados do `seed`.

- **Painel (#20), em `/painel/`:** os indicadores "Itens em estoque" (com a variação em relação ao fim do mês anterior) e "Itens em alerta"; o estoque por categoria, com totais separados por unidade e o percentual de itens acima do mínimo; e os pontos de atenção, com link para a lista de itens. O painel é o mesmo para Voluntário e Administrador.
- **Relatório de distribuições (#21), em `/distribuicoes/relatorio/`:** tabela agrupada por família e item, com categoria, quantidade total, número de distribuições e data do último registro; filtros por período e família, isolados ou combinados; resumo com os totais por unidade e o número de famílias e distribuições; e o botão de exportação CSV, que leva os mesmos filtros. Fica no menu lateral, no grupo Movimentações.
- **Totais por doador e item (#22), em `/doacoes/`:** abaixo dos filtros, a tabela agrupa as doações do período por doador e item, com o total doado, a unidade e o número de doações registradas. Os totais consideram todos os registros filtrados, não só os da página atual.

[GIF ou prints das telas do painel, do relatório de distribuições e dos totais por doador rodando no deploy — gravar até 30/10]

**Como reproduzir localmente** (passo a passo completo no [`README.md`](../../README.md)):

```bash
source .venv/bin/activate
npm install && npm run build
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/login/` com um dos usuários de teste do `seed` (lista em [`README.md` → "Usuários de teste"](../../README.md#usuários-de-teste)). Telas desta sprint: `/painel/`, `/distribuicoes/relatorio/` e `/doacoes/`.

## 3. Backlog atualizado

Link do board: https://github.com/users/Antonio-pf/projects/11

[Print do board no fim da Sprint 4 — capturar até 30/10]

Mudanças de status na Sprint 4, até 29/10/2026:

- **Done:** #20 (painel) e #22 (totais por doador), as duas movidas depois do merge de 28/10/2026.
- **In Progress:** #21 (relatório de distribuições). O código entrou na `main` em 29/10/2026 (PR #53), mas a issue continua aberta e o card ainda não foi movido para "Done". [mover até 30/10]
- **Todo:** #19 (cancelar movimentação), que teve a issue reaberta em 28/10/2026, e #24, que ganhou a issue #50.

## 4. Evidências de teste

121 testes automatizados (`python manage.py test`), 100% passando no commit `58ef94a`, executados em 29/10/2026. São 31 novos nesta sprint: 13 do painel (#20), 3 dos totais por doador (#22), 14 do relatório de distribuições (#21) e 1 dos filtros inválidos (PR #54). Casos do plano de testes que passaram: CT15 (#20), CT16 e CT17 (#21) e CT28 (#22). Continuam pendentes CT20 (#19), CT21 (#23), CT01 e CT08. O CI (jobs `lint` e `test`) passou em todos os merges de 28/10 e 29/10/2026.
Detalhe completo em [`sprint-4-evidencias-teste.md`](sprint-4-evidencias-teste.md).

## 5. Retrospectiva e contribuição individual

- Ata de retrospectiva: [`docs/sprints/sprint-4-retrospectiva.md`](sprint-4-retrospectiva.md)
- Relatórios individuais de contribuição:
  - [Alexandre Ulhoa](sprint-4-contribuicao-alexandre-ulhoa.md)
  - [Daniel Carvalho](sprint-4-contribuicao-daniel-carvalho.md)
  - [Antonio Felipe](sprint-4-contribuicao-antonio-felipe.md)
  - [Luiz Henrique](sprint-4-contribuicao-luiz-henrique.md)

## 6. Riscos/impedimentos para a próxima sprint

- **#19 sem início:** se não for implementada, o corte precisa ser negociado com o professor e registrado. Abandonar a história em silêncio gera penalidade.
- **Revisão e merge semanal:** a `main` ficou de 09/10 a 28/10/2026 sem merge. Dos seis PRs integrados na sprint, só o #49 teve revisão registrada: #46, #47, #51, #53 e #54 entraram sem aprovação de outro integrante.
- **Deploy:** o banco novo do Render é gratuito e expira em 30 dias, por volta de 27/11/2026. A apresentação final é em 13/11/2026.
- **Próximas entregas:** E9 (relatório de testes executados e termo de aceite do cliente, 06/11/2026) e E10 (documentação final, manual do usuário e apresentação, 13/11/2026). Nenhuma das duas foi iniciada.
