# Relatório de Entrega — Sprint 4 — Conecta Social

**Período:** 17/10/2026 a 30/10/2026 (Sprint 4, semanas 11–12)
**Sprint Review:** [data e participantes da Review da Sprint 4 — confirmar com a equipe]

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

> Rascunho escrito em 28/10/2026, com a `main` no commit `410c821`. Atualizar até 30/10/2026 com o que ainda for integrado.

## 1. Planejado vs. entregue

O backlog não registra um planejamento próprio da Sprint 4. A sprint ficou com as histórias que sobraram da Sprint 3 (#19 a #22) e com a #24, que estava sem sprint. [confirmar com a equipe o que foi planejado]

| História (E2) | Planejada para esta sprint? | Entregue? | Observação |
|---|---|---|---|
| #20 — Painel com total de itens em estoque por categoria | Sim (remanescente da Sprint 3) | Sim | PR #47, integrado em 28/10/2026 sem revisão registrada. Mostra os indicadores "Itens em estoque" e "Itens em alerta", o estoque por categoria com o percentual de itens acima do mínimo e os pontos de atenção (até 5 itens de menor saldo), seguindo o frame `2603:39` do protótipo |
| #22 — Histórico de doações por doador com totais por item | Sim (remanescente da Sprint 3) | Sim | PR #49 (Daniel Souza), revisado e aprovado por Antonio Felipe e integrado em 28/10/2026. A tela `/doacoes/` ganhou a tabela "Totais por doador e item", que respeita os filtros de doador e período e exclui as doações canceladas |
| #21 — Relatório de distribuições filtrável por período e família | Sim (remanescente da Sprint 3) | Não (em branch, sem PR) | Implementada por Luiz Henrique no commit `a632519` (19/10/2026), na branch `feature/distribuicoes-historico-estorno`, com a rota `/distribuicoes/relatorio/` e testes. A branch parte de um commit de 24/09 (`3c929e3`), versiona 69 arquivos de `venv/` e não tem PR, então não está na `main` |
| #19 — Cancelar uma movimentação registrada por engano | Sim (remanescente da Sprint 3) | Não | Não iniciada. Issue reaberta e card em "Todo" desde 28/10/2026 |
| #24 — Painel com doações recebidas, famílias atendidas e movimentações recentes | [confirmar] | Não | Ganhou a issue #50 e entrou no board em "Todo" em 28/10/2026 |
| Correções da E4 pedidas pelo professor (README no setup nativo e link único do protótipo) | Sim | Sim | PR #46, integrado em 28/10/2026 sem revisão registrada |
| Correções de forma da E2 e da E3 (título da seção de escopo no termo de aceite e RAs no DDL) | Não | Em revisão | PR #51, aberto em 28/10/2026 e aguardando aprovação |
| Documentos da Sprint 3 (E7), entregues com atraso | Não | Em andamento | Branch `docs/sprint-3` |

## 2. Incremento funcional demonstrável

O sistema está no ar em https://conecta-social-wcxa.onrender.com/. Em 28/10/2026 o deploy estava fora do ar porque o banco PostgreSQL gratuito do Render expirou. Um banco novo foi criado, as migrations rodaram no deploy e o `seed` foi executado. Depois disso, `/health/` respondeu 200, o login com `admin@conectasocial.org` redirecionou para `/painel/` e as telas `/painel/`, `/itens/` e `/distribuicoes/` abriram com os dados do `seed`.

- **Painel (#20), em `/painel/`:** os indicadores "Itens em estoque" (com a variação em relação ao fim do mês anterior) e "Itens em alerta"; o estoque por categoria, com totais separados por unidade e o percentual de itens acima do mínimo; e os pontos de atenção, com link para a lista de itens. O painel é o mesmo para Voluntário e Administrador.
- **Totais por doador e item (#22), em `/doacoes/`:** abaixo dos filtros, a tabela agrupa as doações do período por doador e item, com o total doado, a unidade e o número de doações registradas. Os totais consideram todos os registros filtrados, não só os da página atual.

[GIF ou prints das telas do painel e dos totais por doador rodando no deploy — gravar até 30/10]

**Como reproduzir localmente** (passo a passo completo no [`README.md`](../../README.md)):

```bash
source .venv/bin/activate
npm install && npm run build
python manage.py migrate
python manage.py seed
python manage.py runserver
```

Acesse `http://127.0.0.1:8000/login/` com um dos usuários de teste do `seed` (lista em [`README.md` → "Usuários de teste"](../../README.md#usuários-de-teste)). Telas desta sprint: `/painel/` e `/doacoes/`.

## 3. Backlog atualizado

Link do board: https://github.com/users/Antonio-pf/projects/11

[Print do board no fim da Sprint 4 — capturar até 30/10]

Mudanças de status na Sprint 4, até 28/10/2026:

- **Done:** #20 (painel) e #22 (totais por doador), as duas movidas depois do merge de 28/10/2026.
- **In Progress:** #21 (relatório de distribuições). O código está na branch de Luiz Henrique, sem PR.
- **Todo:** #19 (cancelar movimentação), que teve a issue reaberta em 28/10/2026, e #24, que ganhou a issue #50.

## 4. Evidências de teste

106 testes automatizados (`python manage.py test`), 100% passando no commit `410c821`, executados em 28/10/2026. São 16 novos nesta sprint: 13 do painel (#20) e 3 dos totais por doador (#22). Casos do plano de testes que passaram: CT15 (#20) e CT28 (#22). Continuam pendentes CT16 e CT17 (#21), CT20 (#19), CT21 (#23), CT01 e CT08. O CI (jobs `lint` e `test`) passou nos três merges de 28/10/2026.
Detalhe completo em [`sprint-4-evidencias-teste.md`](sprint-4-evidencias-teste.md).

## 5. Retrospectiva e contribuição individual

- Ata de retrospectiva: [`docs/sprints/sprint-4-retrospectiva.md`](sprint-4-retrospectiva.md)
- Relatórios individuais de contribuição:
  - [Alexandre Ulhoa](sprint-4-contribuicao-alexandre-ulhoa.md)
  - [Daniel Carvalho](sprint-4-contribuicao-daniel-carvalho.md)
  - [Antonio Felipe](sprint-4-contribuicao-antonio-felipe.md)
  - [Luiz Henrique](sprint-4-contribuicao-luiz-henrique.md)

## 6. Riscos/impedimentos para a próxima sprint

- **#21 fora da `main`:** é história "Deve ter". O código de Luiz Henrique precisa virar um PR a partir da `main` atual, sem a pasta `venv/` e com conflitos resolvidos (a branch tem 1 commit sobre a `main` de 24/09), antes do Relatório de Testes Executados (E9, 06/11/2026).
- **#19 sem início:** se não for implementada, o corte precisa ser negociado com o professor e registrado. Abandonar a história em silêncio gera penalidade.
- **Revisão e merge semanal:** a `main` ficou de 09/10 a 28/10/2026 sem merge, e os PRs #46 e #47 entraram sem revisão.
- **Deploy:** o banco novo do Render é gratuito e expira em 30 dias, por volta de 27/11/2026. A apresentação final é em 13/11/2026.
- **Próximas entregas:** E9 (relatório de testes executados e termo de aceite do cliente, 06/11/2026) e E10 (documentação final, manual do usuário e apresentação, 13/11/2026). Nenhuma das duas foi iniciada.
