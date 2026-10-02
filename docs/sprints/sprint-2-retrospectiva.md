<!-- RASCUNHO: revisar com a equipe na retrospectiva de 02/10/2026, ajustar a lista de presentes e remover este comentário antes de abrir o PR. -->
# Ata de Retrospectiva — Sprint 2 — Conecta Social

**Data:** 02/10/2026
**Presentes:** Alexandre Ulhoa (RA 2840482423007) — Daniel Carvalho (RA 2840482211052) — Cintia Oliveira (RA 2840482421017) — Antonio Felipe (RA 2840482211003) — Luiz Henrique (RA 2840482423005)

## 1. Ações da retrospectiva anterior — foram aplicadas?

| Ação decidida | Aplicada? | Evidência/comentário |
|---|---|---|
| Nenhum PR é mesclado sem aprovação registrada no GitHub por outro integrante | Não | Os PRs #34 e #35 foram mesclados sem revisão registrada (o #34 pelo próprio autor) e a história #14 entrou na `main` por merge direto, sem PR (commit `3c929e3`). Houve revisão informal do PR #31, sem registro no GitHub |
| Mover o card para "Done" apenas depois do merge na `main` | Parcialmente | Em 30/09 e 01/10 o board foi reconciliado: #15 a #18 estavam "In Progress" com código mesclado, e #19 estava "Done" sem código na `main` |
| Adicionar teste automatizado para a expiração de sessão por inatividade (CT01) | Não | Nenhum teste de expiração na suíte de 79 testes |
| Estabilizar o deploy público no Render | Parcialmente | Em 01/10/2026 `/health/` respondeu 200 e as rotas `/doacoes/` e `/distribuicoes/` existem no deploy; a primeira resposta após inatividade levou cerca de 20 s |

## 2. O que funcionou bem

- As 5 histórias planejadas (#14 a #18) e as 9 remanescentes da Sprint 1 (#5 a #13) estão na `main`,
  com 79 testes passando (31 novos nesta sprint)
- A regra de negócio central funciona: a distribuição é bloqueada quando o saldo não cobre a
  quantidade ("Saldo insuficiente: disponível X, solicitado Y"), e o saldo do item aparece no
  formulário antes de enviar
- Os dois históricos (doações e distribuições) saíram juntos e reutilizam o mesmo padrão de filtros
  por pessoa e período, com testes dos filtros isolados e combinados
- A requisição de cada história foi documentada no fluxo AI-DLC antes da implementação, o que
  tornou explícitas decisões como aceitar quantidade decimal (kg, l)

## 3. O que não funcionou

- A ação mais importante da retrospectiva anterior (revisão obrigatória de PR) não foi aplicada: o
  histórico da Sprint 2 repete o problema da Sprint 1
- O board ficou desatualizado em relação ao repositório nos dois sentidos (cards "Done" sem código e
  cards "In Progress" já mesclados), e só foi reconciliado no fim da sprint
- Os testes não pegaram um defeito visível no navegador: a data padrão "hoje" era definida no
  formulário, mas o campo abria vazio (formato de data incompatível com `type="date"`). Foi
  achado na gravação dos GIFs e corrigido em 01/10/2026, com testes de regressão
- Depois de registrar uma doação não há mensagem de sucesso; o formulário volta vazio
- A Sprint 3 chega com 5 histórias e duas "Deve ter" (#20 e #21) ainda sem início

## 4. Ações para a próxima sprint

| Ação | Responsável |
|---|---|
| Bloquear o merge na `main` sem aprovação de outro integrante (proteção de branch no GitHub) e registrar a revisão no PR | Equipe |
| Atualizar o board no mesmo dia do merge, e conferir o board contra a `main` na véspera da aula | Equipe |
| Abrir o PR da correção da data padrão "hoje" (já feita) e acrescentar mensagem de sucesso nos formulários de doação e distribuição | Antonio Felipe |
| Escrever os testes pendentes: expiração de sessão (CT01) e paginação de famílias (CT08) | Qualidade |
| Dividir a Sprint 3 por pessoa já na primeira aula: #20 e #21 (consultas agregadas) primeiro, #19, #22 e #23 depois | Equipe |
