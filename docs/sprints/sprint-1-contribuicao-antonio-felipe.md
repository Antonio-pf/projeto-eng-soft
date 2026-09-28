# Relatório Individual de Contribuição — Sprint 1 — Antonio Pires Felipe (RA 2840482211003)

**Papel nesta sprint:** Product Owner

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| Setup do projeto: estrutura inicial, infra e persistência, página inicial e CI (história #0 do board) | `d268065`, `8273a34` — PR #25 | Concluído |
| Telas de login e criação de usuários (sidebar interna, formulário restrito a Administrador) | `62c81bc` | Concluído |
| Autenticação por sessão, logout e controle de perfil | `2ba672d` | Concluído |
| Desativar/reativar usuário sem excluí-lo (história #4 do backlog) | `d7c8fd3` — PR #29 | Concluído |
| Layout no Figma e design system consistente para as telas novas (feito em conjunto com a equipe) | `b98f175` | Concluído |
| Pipeline de CI (cache Docker, jobs de execução, template de PR) | `e0b5682`, `01a5b0d`, `274caf6` | Concluído |
| Relatório de entrega e evidências de teste da Sprint 1 (E5) | `dabc859` | Concluído |


## 2. Rituais que participei

- [x] Dailies/weeklies
- [x] Sprint Review
- [x] Retrospectiva

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| PR #30 — Feature/historia 5 cadastro doador | Daniel Carvalho | Revisei e aprovei o cadastro de doador (história #5); sem observações adicionais apenas alguns conflitos de arquivos, aprovado direto. |
| PR #31 — Feature/setup projeto (CRUD doador/família/categoria/item) | Luiz Henrique Neres | Revisão informal/local: entrei na branch, testei e conferi que estava tudo ok antes de ir pra main. Sem aprovação formal registrada no GitHub — o próprio Luiz abriu e mesclou o PR. |


## 4. Dificuldades e o que aprendi

A principal dificuldade foi ter que voltar a autenticação customizada para o
sistema nativo do Django — retrabalho que poderia ter sido evitado com um
conhecimento prévio maior sobre o sistema de auth nativo, que só adquiri
durante a própria sprint. Também tive dificuldades no deploy: o serviço de
hospedagem apresentou alguns erros, e o aprendizado foi entender melhor o que
era necessário para rodar a aplicação nele.
