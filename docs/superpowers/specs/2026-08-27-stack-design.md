# Design da Stack Tecnológica — Sistema de Gestão de ONG de Doações

**Data:** 2026-08-27
**Equipe:** Alexandre Ulhoa, Daniel Carvalho, Cintia Oliveira, Antonio Felipe
**Status:** Aprovado pela equipe — referência para o Termo de Aceite (E2)

---

## 1. Stack tecnológica

| Camada | Escolha | Justificativa |
|---|---|---|
| Backend | Django (Python) | Equipe já conhece Python; auth/permissões, ORM e migrations built-in |
| Frontend | Django Templates | HTML server-side; equipe já conhece HTML/CSS/JS vanilla — sem framework JS |
| Estilização | Tailwind CSS via CDN + daisyUI via CDN | Zero configuração local; componentes prontos (botões, tabelas, modais, badges) |
| Banco de dados | PostgreSQL | Suporte a FK, CHECK constraint (saldo ≥ 0), GROUP BY e JOINs complexos |
| Deploy | Render (Web Service + PostgreSQL) | Free tier, deploy automático via push no GitHub, URL pública gerada |
| Repositório | Monorepo único | Estrutura natural do Django — front e back no mesmo projeto |

### Por que não outras opções

- **Netlify:** feito para sites estáticos e serverless; não suporta Django (processo Python contínuo)
- **Django REST + Vanilla JS:** CORS, gerenciamento de token e dois deploys adicionam risco desnecessário para equipe majoritariamente iniciante
- **Next.js + Supabase:** exige React, que nenhum membro da equipe domina

---

## 2. Estrutura de apps Django

O projeto é dividido em 4 apps, equilibrando separação de responsabilidades com baixo overhead de boilerplate para iniciantes.

```
ong_doacoes/          ← projeto Django (settings, urls raiz, wsgi)
├── accounts/         ← autenticação, login/logout, perfis Administrador e Voluntário
├── core/             ← cadastros: Doador, Família, CategoriaItem, Item
├── movimentacoes/    ← Doação (entrada de estoque) e Distribuição (saída), regra de saldo
└── relatorios/       ← dashboard de indicadores e relatórios filtráveis
```

**Divisão por responsabilidade:**

- `accounts` — isolado por ser código sensível; todo PR aqui exige revisão cuidadosa pelo Responsável por Qualidade
- `core` — agrupa os CRUDs simples sem regra de negócio complexa; ponto de entrada para membros iniciantes
- `movimentacoes` — concentra a regra de negócio crítica (verificação de saldo antes de distribuição); isolada para facilitar testes unitários
- `relatorios` — queries complexas (`GROUP BY`, `JOIN` de 4+ tabelas) separadas para não poluir os outros apps

**Mapeamento apps → sprints:**

| Sprint | Entrega | Apps principais |
|---|---|---|
| Sprint 1 (E5) | Fundação e CRUD | `accounts` + `core` |
| Sprint 2 (E6) | Regra de negócio | `movimentacoes` |
| Sprint 3 (E7) | Relatórios e perfis | `relatorios` |
| Sprint 4 (E8) | Requisitos não funcionais | todos |

---

## 3. Estrutura do repositório

```
ong-doacoes/
├── manage.py
├── requirements.txt          ← django, gunicorn, psycopg2-binary, python-decouple
├── runtime.txt               ← python-3.12.x
├── .env.example              ← SECRET_KEY, DATABASE_URL, DEBUG (sem valores reais)
├── .gitignore                ← .env, __pycache__, db.sqlite3, staticfiles/
├── README.md                 ← setup local, pré-requisitos, link do deploy
│
├── ong_doacoes/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/
├── core/
├── movimentacoes/
├── relatorios/
│
├── static/
│   └── js/                   ← vanilla JS leve (validações de form, interações simples)
│
└── templates/
    ├── base.html             ← CDN Tailwind + daisyUI, navbar, sidebar, blocos base
    ├── accounts/
    ├── core/
    ├── movimentacoes/
    └── relatorios/
```

**Regra de segurança:** `.env` nunca entra no repositório. O `.env.example` documenta as variáveis necessárias sem os valores. Credenciais ficam exclusivamente nas variáveis de ambiente do Render.

---

## 4. Configuração do deploy no Render

### Passo a passo de criação

1. Criar recurso **PostgreSQL** primeiro — o Render gera a `DATABASE_URL` automaticamente
2. Criar recurso **Web Service** apontando para o repositório GitHub (branch `main`)

### Comandos do Web Service

| Campo | Valor |
|---|---|
| **Build command** | `pip install -r requirements.txt && python manage.py migrate && python manage.py collectstatic --no-input` |
| **Start command** | `gunicorn ong_doacoes.wsgi` |

### Variáveis de ambiente (configurar no painel do Render)

| Variável | Descrição |
|---|---|
| `SECRET_KEY` | String aleatória longa (gerar com `python -c "import secrets; print(secrets.token_hex(50))"`) |
| `DATABASE_URL` | Copiada do recurso PostgreSQL criado no passo 1 |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `ong-doacoes.onrender.com` |

### CI/CD automático

A cada `git push` na branch `main`, o Render detecta a mudança, executa o build command (instala dependências, roda migrations, coleta estáticos) e reinicia o serviço. Esse fluxo serve como evidência de CI/CD para os relatórios de sprint (E5–E8).

```
git push → Render detecta → build → migrate → collectstatic → restart
```

### Limitação do free tier

O serviço hiberna após 15 minutos sem acesso — o primeiro request demora ~30 segundos para "acordar". Não afeta a avaliação; é comportamento esperado e documentado.

O banco PostgreSQL free expira em 90 dias. Com 14 semanas de semestre (~98 dias), será necessário recriar o banco uma vez e rodar o seed novamente. Adicionar lembrete no calendário da equipe na semana 11.
