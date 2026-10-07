# Relatório Individual de Contribuição — Sprint 1 — Luiz Henrique Neres (RA 2840482423005)

# Relatório Individual de Contribuição — Sprint 2 — Luiz Henrique Neres (RA 2840482423005)
**Papel nesta sprint:** Desenvolvedor Full-Stack

## 1. O que fiz

| Item | PR/commit | Status |
| :--- | :--- | :--- |
| Implementação de cadastros, listagens e testes unitários/integração para Doadores, Famílias, Categorias e Itens | `4a28255` | Mergeado |
| Atualização e validação de testes de sistema e fluxos no Django (`core/tests.py`) | `core/tests.py` | Mergeado |
| Revisão e refatoração de formulários, views e templates HTML para os módulos do sistema | `core/forms.py` | Mergeado |

## 2. Rituais que participei

- [x] Dailies/weeklies
- [x] Sprint Review
- [x] Retrospectiva

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
| :--- | :--- | :--- |
| #28, #29, #30, #32 | Antonio Pires e Equipe | Validei a segurança de rotas, a padronização do layout com sidebar e correções nos fluxos de cadastro |

## 4. Dificuldades e o que aprendi

Subestimei a complexidade de garantir a robustez das validações de CPF/CNPJ e a integridade relacional entre modelos acoplados (Doadores, Famílias, Itens e Distribuições) dentro dos testes automatizados. O uso do ORM do Django exigiu um estudo mais refinado na estruturação de ModelForms e no isolamento de cenários de teste para prevenir regressões de forma eficiente.

