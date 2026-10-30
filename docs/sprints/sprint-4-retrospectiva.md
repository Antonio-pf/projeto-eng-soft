# Ata de Retrospectiva — Sprint 4 — Conecta Social

**Data:** 23/10/2026, encontro online
**Presentes:** [confirmar quem esteve presente] Alexandre Ulhoa (RA 2840482423007) — Daniel Carvalho (RA 2840482211052) — Antonio Felipe (RA 2840482211003) — Luiz Henrique (RA 2840482423005)

> Rascunho preparado em 28/10/2026 e atualizado em 29/10/2026 a partir do histórico do repositório e do board. As seções 2, 3 e 4 precisam ser revistas e completadas pela equipe em conjunto, depois da Review.

## 1. Ações da retrospectiva anterior — foram aplicadas?

| Ação decidida | Aplicada? | Evidência/comentário |
|---|---|---|
| Nenhum merge sem aprovação registrada no GitHub por outro integrante | Parcialmente | O PR #49 foi aprovado por Antonio Felipe antes do merge. Os PRs #46 e #47 (28/10/2026) e #51, #53 e #54 (29/10/2026) entraram sem revisão |
| Merge na `main` pelo menos uma vez por semana | Não | Não houve merge entre 09/10 e 28/10/2026 |
| Terminar a #21 com os testes CT16 e CT17 | Sim, no fim da sprint | Luiz Henrique implementou o relatório em 19/10/2026 numa branch sem PR e o refez a partir da `main` atual em 28/10/2026 (commit `56ce3c6`). Antonio Felipe alinhou a tela ao protótipo e completou os testes (commit `d8c463f`). Entrou na `main` em 29/10/2026 pelo PR #53, com CT16 e CT17 passando, mas sem revisão |
| Implementar a #19 ou negociar o corte com o professor | Não | Nenhum código, e nenhum registro de negociação |
| Escrever o teste da exportação CSV (CT21) e os pendentes CT01 e CT08 | Não | Nenhum dos três existe no commit `58ef94a`. Para o CSV, só há o teste de que o link do relatório leva os filtros |
| Checar o deploy antes de cada aula e anotar a data de expiração do banco | Parcialmente | A queda só foi percebida em 28/10/2026. O banco foi recriado no mesmo dia, e a nova expiração fica por volta de 27/11/2026 |
| Fechar os documentos da sprint até a véspera do prazo | [confirmar em 30/10] | Os documentos da Sprint 3 foram escritos com atraso, em 28/10/2026 |

## 2. O que funcionou bem

- As três histórias de consulta agregada que estavam atrasadas (#20, #21 e #22) entraram na `main`, com 30 testes novos e o CI verde
- O PR #49, de Daniel Carvalho, foi o primeiro PR de código da sprint com revisão registrada antes do merge
- O deploy foi recuperado no mesmo dia em que a queda foi percebida, e a produção voltou com dados de demonstração
- O board foi reconciliado com a `main`: #19 reaberta e #24 com card
- [completar com a equipe]

## 3. O que não funcionou

- O trabalho de Luiz Henrique na #21 ficou 9 dias em uma branch sem PR. Ninguém viu, e ninguém revisou. Quando virou PR, entrou na `main` no último dia, também sem revisão
- A `main` ficou quase 3 semanas sem merge, e os PRs prontos esperaram revisão até o fim da sprint
- A #19 passou por duas sprints sem responsável
- Os testes pendentes desde a Sprint 2 (CT01 e CT08) continuam sem dono
- [completar com a equipe]

## 4. Ações para a próxima sprint

| Ação | Responsável |
|---|---|
| Decidir a #19 até a próxima aula: implementar com CT20 ou negociar o corte com o professor | [responsável] |
| Escrever CT21, CT01 e CT08 e consolidar o Relatório de Testes Executados (E9, 06/11/2026) | [responsável — papel de Qualidade] |
| Conseguir o termo de aceite assinado pelo cliente (E9) | [responsável] |
| Toda branch com trabalho vira PR no mesmo dia, mesmo como rascunho (draft) | Equipe |
| Revisar os PRs abertos em até 2 dias. Merge na `main` toda semana | Equipe |
