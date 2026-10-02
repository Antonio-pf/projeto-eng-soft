# Ata de Retrospectiva — Sprint 1 — Conecta Social

**Data:** 18/09/2026
**Presentes:** Alexandre Ulhoa (RA 2840482423007) — Daniel Carvalho (RA 2840482211052) — Cintia Oliveira (RA 2840482421017) — Antonio Felipe (RA 2840482211003) — Luiz Henrique (RA 2840482423005)

## 1. Ações da retrospectiva anterior — foram aplicadas?

| Ação decidida | Aplicada? | Evidência/comentário |
|---|---|---|
| _(Sprint 1 é a primeira — não há retrospectiva anterior)_ | — | — |

## 2. O que funcionou bem

- As 4 histórias de autenticação e perfis (#1 a #4) foram entregues dentro da sprint, com GIFs de
  demonstração e 26 testes automatizados passando
- Pipeline de CI e template de PR no ar desde o início, e o layout das telas definido no Figma antes
  da implementação, com design system consistente entre as telas novas

## 3. O que não funcionou

- Só 4 das 13 histórias planejadas (#1 a #13) ficaram prontas; #5 a #13 passaram para a Sprint 2
- Retrabalho na autenticação: foi preciso voltar da autenticação customizada para o sistema nativo
  do Django, por falta de conhecimento prévio sobre o auth nativo
- O serviço de hospedagem apresentou erros no deploy
- O PR #31 foi aberto e mesclado pelo mesmo autor, sem aprovação formal no GitHub
- Cards do board ficaram marcados como "Done" sem código correspondente na `main`

## 4. Ações para a próxima sprint

| Ação | Responsável |
|---|---|
| Nenhum PR é mesclado sem aprovação registrada no GitHub por outro integrante | Equipe |
| Mover o card para "Done" apenas depois do merge na `main` | Equipe |
| Adicionar teste automatizado para a expiração de sessão por inatividade (CT01) | Qualidade |
| Estabilizar o deploy público no Render | Equipe |
