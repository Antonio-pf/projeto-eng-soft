# Conecta Social

Sistema web de gestão operacional para ONGs de doações. O sistema acompanha o ciclo dos itens recebidos, desde o registro da doação até a distribuição para famílias beneficiadas.

**Deploy:** [https://conecta-social-wcxa.onrender.com/](https://conecta-social-wcxa.onrender.com/)

**Equipe:** Alexandre Victoriano Ribeiro Ulhoa (RA 2840482423007) — Daniel Souza Monteiro de Carvalho (RA 2840482211052) — Antonio Pires Felipe (RA 2840482211003) — Luiz Henrique Neres (RA 2840482423005) · Laboratório de Engenharia de Software · ADS Fatec Ribeirão Preto

## Stack

- Frontend: Django Templates + Tailwind CSS 3.4.17 + daisyUI 4.12.10, compilados em um único CSS (`npm run build`), e htmx 2.0.11, versionado em `static/js/htmx.min.js`, sem CDN
- Backend: Python 3.12+ + Django 5.2+
- Banco de dados: PostgreSQL 15+

## Como rodar localmente

### Pré-requisitos

- Git 2.30+
- Python 3.12+
- pip 24+
- PostgreSQL 15+
- `venv`, incluído no Python
- Node.js 18+ e npm 9+ (só para compilar o CSS)
- Docker Engine 24+ e Docker Compose v2+ (opcional)

### Passo a passo

1. Clone o repositório: `git clone https://github.com/Antonio-pf/projeto-eng-soft.git` e entre na pasta com `cd projeto-eng-soft`.

2. Crie e ative um ambiente virtual e instale as dependências:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # Linux/macOS
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

   No Windows PowerShell, crie e ative o ambiente com `py -3.12 -m venv .venv` e `.venv\Scripts\Activate.ps1`; no `cmd.exe`, com `py -3.12 -m venv .venv` e `.venv\Scripts\activate.bat`. Depois rode os mesmos comandos `pip`.

3. Configure as variáveis de ambiente (copie `.env.example` para `.env` e preencha). O arquivo `.env.example` contém apenas valores de exemplo e nunca deve receber credenciais reais. Gere uma `SECRET_KEY` exclusiva com:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   O projeto não lê o `.env` automaticamente: defina as variáveis no terminal antes de executar o Django.

   Linux/macOS (Bash ou Git Bash):

   ```bash
   cp .env.example .env
   set -a
   source .env
   set +a
   ```

   No PowerShell:

   ```powershell
   Copy-Item .env.example .env
   $env:SECRET_KEY = "<cole-o-valor-gerado-aqui>"
   $env:DEBUG = "True"
   $env:ALLOWED_HOSTS = "localhost,127.0.0.1"
   $env:DATABASE_URL = "postgresql://conecta:conecta@localhost:5432/conectasocial"
   ```

   No `cmd.exe`:

   ```cmd
   copy .env.example .env
   set SECRET_KEY=<cole-o-valor-gerado-aqui>
   set DEBUG=True
   set ALLOWED_HOSTS=localhost,127.0.0.1
   set DATABASE_URL=postgresql://conecta:conecta@localhost:5432/conectasocial
   ```

   | Variável | Descrição |
   |---|---|
   | `SECRET_KEY` | Chave usada pelo Django. Gere uma chave exclusiva com o comando acima e mantenha-a fora do repositório. Exemplo local: `django-insecure-<valor-gerado-localmente>` |
   | `DEBUG` | Ativa o modo de desenvolvimento. Exemplo local: `True` |
   | `ALLOWED_HOSTS` | Hosts aceitos pelo Django, separados por vírgula. Exemplo local: `localhost,127.0.0.1` |
   | `DATABASE_URL` | URL de conexão com o PostgreSQL local. Exemplo local: `postgresql://conecta:conecta@localhost:5432/conectasocial` |

4. Crie o banco e rode o schema: crie o usuário e o banco PostgreSQL local (os mesmos `conecta`/`conecta` da `DATABASE_URL` e do `compose.yaml`). Os comandos são os mesmos no Linux/macOS, no Git Bash, no PowerShell e no `cmd.exe`:

   ```bash
   psql -U postgres -c "CREATE USER conecta WITH PASSWORD 'conecta' CREATEDB;"
   psql -U postgres -c "CREATE DATABASE conectasocial OWNER conecta;"
   ```

   O PostgreSQL precisa estar instalado, em execução e disponível no `PATH`. O usuário `postgres` é o administrador criado na instalação; o `psql` pode pedir a senha dele. A permissão `CREATEDB` do usuário `conecta` é necessária para o `python manage.py test` criar o banco de testes. Se `psql` não for reconhecido, adicione a pasta `bin` da instalação do PostgreSQL ao `PATH` ou use o Docker Compose (passo 6). O schema é criado pelas migrations no passo 5; o `db/schema.sql` é o DDL de referência da E3.

5. Rode as migrations e o seed: `python manage.py migrate` e `python manage.py seed`. As migrations em `core/migrations/` são a fonte oficial da estrutura do banco. O `seed` pode ser executado novamente sem duplicar os dados e cria os usuários `admin@conectasocial.org` (Administrador), `maria@conectasocial.org` e `joao@conectasocial.org` (Voluntário), todos com a senha `alterar-senha`. A aplicação também possui fallback para `db.sqlite3` quando `DATABASE_URL` não está definida, mas o fluxo documentado usa PostgreSQL.

6. Suba o projeto: compile o CSS (Tailwind + daisyUI) e inicie o servidor.

   ```bash
   npm ci
   npm run build
   python manage.py runserver
   ```

   O `npm run build` gera `static/css/tailwind.css`, que não é versionado; sem ele, as páginas abrem sem estilo. Ao editar templates ou classes em `core/forms.py`, deixe `npm run dev` rodando em outro terminal. O htmx já está versionado; para atualizar a versão, altere `htmx.org` no `package.json` e rode `npm install` seguido de `npm run htmx`.

   Alternativa com Docker (opcional): `docker compose up --build` cria o PostgreSQL e a aplicação, roda `migrate` e `seed` e compila o CSS, sem instalar Python, PostgreSQL ou Node na máquina (no Windows, abra o Docker Desktop antes). Para parar, `docker compose down`; para apagar também os dados do PostgreSQL local, `docker compose down -v`. O deploy atual usa o ambiente Python nativo configurado em `render.yaml`.

7. Acesse em `http://127.0.0.1:8000`.

## Estrutura do repositório

```text
/conecta/             — configurações do projeto Django
/core/                — aplicação Django e views principais
/templates/           — templates HTML da aplicação
/static/              — CSS e arquivos estáticos (`static/src/tailwind.css` é a entrada do build do CSS)
/db/                  — schema SQL de referência legada
/core/migrations/     — migrations oficiais do banco
/core/management/     — comandos Django, incluindo o seed
/docs/                — visão, backlog, UML, DER, testes e protótipo
/.github/workflows/   — workflow de CI do GitHub Actions
/Dockerfile           — imagem Docker da aplicação
/compose.yaml          — aplicação e PostgreSQL locais via Docker Compose
/scripts/             — scripts de qualidade, incluindo validação de commits
.env.example          — modelo das variáveis de ambiente, sem segredos
manage.py             — ponto de entrada do Django
package.json          — build do CSS (Tailwind + daisyUI) e cópia do htmx via npm
tailwind.config.js    — arquivos varridos pelo Tailwind e plugin daisyUI
requirements.txt      — dependências Python
render.yaml           — configuração de deploy no Render
```

## Convenções da equipe

- Branches: `feature/nome-da-feature`, `fix/nome-do-problema` e `docs/nome-do-documento`, sempre criadas a partir de `main`.
- Commits: Conventional Commits, no formato `<tipo>(escopo-opcional): <descrição>`, com os tipos `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style` e `test` (validados pelo hook `pre-commit install --hook-type commit-msg`).
- Toda PR exige revisão de ao menos 1 integrante antes do merge.

## Testes

Como rodar: `coverage run manage.py test` seguido de `coverage report`, que falha se a cobertura ficar abaixo de 95%, o mínimo exigido no CI ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)).

## Licença / Uso acadêmico

Projeto desenvolvido para a disciplina de Laboratório de Engenharia de Software — ADS, Fatec Ribeirão Preto, 2026.
