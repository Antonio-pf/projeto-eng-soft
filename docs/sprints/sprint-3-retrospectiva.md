# Ata de Retrospectiva — Sprint 3 — Conecta Social

**Data:** 16/10/2026, encontro online
**Presentes:** [confirmar quem esteve presente] Alexandre Ulhoa (RA 2840482423007) — Daniel Carvalho (RA 2840482211052) — Antonio Felipe (RA 2840482211003) — Luiz Henrique (RA 2840482423005)

> Rascunho preparado em 28/10/2026 a partir do histórico do repositório e do board. As seções 2, 3 e 4 precisam ser revistas e completadas pela equipe em conjunto.

## 1. Ações da retrospectiva anterior — foram aplicadas?

| Ação decidida | Aplicada? | Evidência/comentário |
|---|---|---|
| Atualizar o board no mesmo dia do merge e conferir o board contra a `main` na véspera da aula | Não | Em 28/10/2026 a issue da #19 estava fechada com o card em "Todo" e sem código na `main`, e a #24 não tinha card. Os cards foram corrigidos nesse dia |
| Abrir o PR da correção da data padrão "hoje" e acrescentar mensagem de sucesso nos formulários de doação e distribuição | Sim | PR #38 (02/10/2026), com o teste de regressão `test_formulario_abre_com_data_de_hoje_em_formato_iso`. As views de doação e distribuição mostram "Doação registrada com sucesso!" e "Distribuição registrada com sucesso!" |
| Escrever os testes pendentes de expiração de sessão (CT01) e paginação de famílias (CT08) | Não | Não há teste de expiração de sessão nem de paginação de famílias no commit `76acbde` |
| Dividir a Sprint 3 por pessoa na primeira aula: #20 e #21 primeiro, depois #19, #22 e #23 | [confirmar] | Pelo histórico, a #20 foi feita por Antonio Felipe (PR #47) e a #22 por Daniel Carvalho (PR #49), as duas depois do prazo. A #21 e a #19 não tiveram responsável que abrisse PR |

## 2. O que funcionou bem

- A #20 (painel por categoria com pontos de atenção) foi implementada e seguiu o frame `2603:39` do protótipo. O PR #47 foi aberto em 09/10/2026, dentro da sprint
- A ação da data padrão e da mensagem de sucesso, decidida na Sprint 2, foi aplicada já no começo da sprint, com teste de regressão
- O CI segurou a qualidade do que entrou: `lint` e `test` passaram em todos os merges da `main`
- As duas correções pedidas pelo professor na E4 (README no setup nativo e link do protótipo) foram feitas no PR #46, aberto em 08/10/2026
- [completar com a equipe]

## 3. O que não funcionou

- Só uma das 5 histórias planejadas (#23) estava na `main` no prazo, e ela não tem teste. #20 e #22 ficaram prontas depois do prazo
- A `main` ficou sem merge de 09/10 a 28/10/2026. Os PRs #46 e #47 esperaram 19 dias e acabaram integrados sem revisão
- A revisão obrigatória de PR, a ação mais repetida desde a Sprint 1, continua sem ser cumprida: dos PRs integrados na sprint, só #43 e #45 tiveram revisão registrada
- Os documentos da Sprint 3 não foram entregues no prazo da E7 (16/10/2026)
- O banco gratuito do Render expirou durante a sprint e ninguém percebeu que o deploy tinha caído
- O código da sprint ficou concentrado em uma pessoa: todos os PRs de código integrados na sprint foram abertos por Antonio Felipe
- [completar com a equipe]

## 4. Ações para a próxima sprint

| Ação | Responsável |
|---|---|
| Nenhum merge sem aprovação registrada no GitHub por outro integrante. Pedir revisão no mesmo dia em que o PR é aberto | Equipe |
| Merge na `main` pelo menos uma vez por semana. Na véspera da aula, conferir se há PR parado esperando revisão | [responsável] |
| Terminar a #21 (tabela agregada, seguindo o frame `2603:727`), com testes CT16 e CT17 | [responsável] |
| Implementar a #19 (cancelamento com reversão de saldo e CT20) ou negociar o corte com o professor antes da Semana 11 | [responsável] |
| Escrever o teste da exportação CSV (CT21) e os pendentes CT01 e CT08 | [responsável — papel de Qualidade] |
| Checar o deploy (`/health/` e login) antes de cada aula e anotar no calendário a nova data de expiração do banco (~27/11/2026) | [responsável] |
| Fechar os documentos da sprint até a véspera do prazo, com cada integrante abrindo o PR do próprio relatório individual | Equipe |
