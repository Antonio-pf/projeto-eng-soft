# Relatório Individual de Contribuição — Sprint 2 — Luiz Henrique Neres (RA 2840482423005)

**Papel nesta sprint:** Desenvolvedor Full-Stack / QA

## 1. O que fiz

| Item | PR/commit | Status |
|---|---|---|
| Implementação de cadastros, listagens e formulários para Doadores, Famílias, Categorias e Itens | [`core/views.py`](../../core/views.py), [`core/forms.py`](../../core/forms.py) | Concluído |
| Criação e expansão da suíte de testes unitários e de integração no Django (`core/tests.py`) | [`core/tests.py`](../../core/tests.py) | Concluído |
| Refatoração de rotas e mapeamento de URLs para os novos módulos do sistema | [`core/urls.py`](../../core/urls.py) | Concluído |
| Ajustes e melhorias em templates HTML, formulários e integração com o painel administrativo | [`templates/core/doador_form.html`](../../templates/core/doador_form.html) | Concluído |

## 2. Rituais que participei

- [x] Planejamento da Sprint (Sprint Planning)
- [x] Reuniões diárias e alinhamentos semanais (Dailies/Weeklies)
- [x] Revisão da Sprint (Sprint Review)
- [x] Retrospectiva da Sprint

## 3. PRs de colegas que revisei

| PR | Autor | Comentário resumido |
|---|---|---|
| [`PR #28`, `#29`, `#30`, `#32`](../../core/views.py) | Antonio Pires e Equipe | Revisão de autenticação, painel administrativo, layout responsivo com sidebar e validações de cadastros |

## 4. Dificuldades e o que aprendi

- **Dificuldade:** Garantir a consistência de relacionamentos complexos entre modelos no banco de dados e cobertura robusta de testes para validação de formulários.
- **Aprendizado:** Domínio avançado do Django ORM, construção de testes automatizados eficientes, uso de `ModelForm` e boas práticas de desenvolvimento full-stack para aplicações web.
