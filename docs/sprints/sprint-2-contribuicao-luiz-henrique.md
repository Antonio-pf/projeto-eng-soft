# Relatório Individual de Contribuição — Sprint 2 — Luiz Henrique Neres (RA 2840482423005)

**Papel nesta sprint:** Desenvolvedor / Desenvolvedor Full-Stack

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| Implementação de cadastros, listagens e testes unitários/integração para Doadores, Famílias, Categorias e Itens | [`4a28255`](../../core/views.py) | Concluído |
| Atualização e validação de testes de sistema e fluxos no Django (`core/tests.py`) | [`core/tests.py`](../../core/tests.py) | Concluído |
| Revisão e refatoração de formulários, views e templates HTML para os módulos do sistema | [`core/forms.py`](../../core/forms.py) | Concluído |

## 2. Rituais que participei

- [x] Dailies/weeklies
- [x] Sprint Review
- [x] Retrospectiva

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| [`PR #28`, `#29`, `#30`, `#32`](../../core/views.py) | Equipe (Antonio Pires e demais) | Revisão de autenticação, painel, layout com sidebar e correções de cadastros |

## 4. Dificuldades e o que aprendi

- **Dificuldade:** Garantir a robustez das validações de CPF/CNPJ e integridade relacional entre modelos complexos (Doadores, Famílias, Itens e Distribuições) nos testes automatizados.
- **Aprendizado:** Domínio avançado sobre o ORM do Django, estruturação de formulários baseados em ModelForm e criação de suítes de testes abrangentes no Django para validação de regras de negócio.
