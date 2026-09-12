# Conecta Social

Sistema web de gestão operacional para ONGs de doações. O sistema acompanha o ciclo dos itens recebidos, desde o registro da doação até a distribuição para famílias beneficiadas.

**Deploy:** [https://conecta-social-wcxa.onrender.com/](https://conecta-social-wcxa.onrender.com/)

**Equipe:**
- Alexandre Victoriano Ribeiro Ulhoa — RA 2840482423007
- Daniel Souza Monteiro de Carvalho — RA 2840482211052
- Cintia Marcelo de Oliveira — RA 2840482421017
- Antonio Pires Felipe — RA 2840482211003
- Luiz Henrique Neres — RA 2840482423005

## Stack

- Frontend: Django Templates + Tailwind CSS via CDN + daisyUI 4.12.10 via CDN
- Backend: Python 3.12+ + Django 5.2+
- Banco de dados: PostgreSQL 15+
- Deploy: Render Web Service + PostgreSQL

## Como rodar localmente

### Pré-requisitos

- Git 2.30+
- Python 3.12+
- pip 24+
- PostgreSQL 15+
- `venv`, incluído no Python
- Docker Engine 24+ e Docker Compose v2+ (opcional)

### Passo a passo

1. Clone o repositório:

   ```bash
   git clone https://github.com/Antonio-pf/projeto-eng-soft.git
   cd projeto-eng-soft
   ```

2. Crie e ative um ambiente virtual:

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate       # Linux/macOS
   ```

   No Windows PowerShell:

   ```powershell
   py -3.12 -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   No Windows `cmd.exe`:

   ```cmd
   py -3.12 -m venv .venv
   .venv\Scripts\activate.bat
   ```

3. Instale as dependências:

   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente obrigatórias. O arquivo `.env.example` contém apenas valores de exemplo e nunca deve receber credenciais reais:

   Gere uma `SECRET_KEY` exclusiva para o ambiente local com o Django:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

   Copie o valor exibido para `SECRET_KEY` no arquivo `.env`.

   Linux/macOS (Bash ou Git Bash):

   ```bash
   cp .env.example .env
   set -a
   source .env
   set +a
   ```

   No PowerShell, copie o modelo e defina as variáveis na sessão atual:

   ```powershell
   Copy-Item .env.example .env
   $env:SECRET_KEY = "<cole-o-valor-gerado-aqui>"
   $env:DEBUG = "True"
   $env:ALLOWED_HOSTS = "localhost,127.0.0.1"
   $env:DATABASE_URL = "postgresql://conecta:conecta@localhost:5432/conectasocial"
   ```

   No `cmd.exe`, use:

   ```cmd
   copy .env.example .env
   set SECRET_KEY=<cole-o-valor-gerado-aqui>
   set DEBUG=True
   set ALLOWED_HOSTS=localhost,127.0.0.1
   set DATABASE_URL=postgresql://conecta:conecta@localhost:5432/conectasocial
   ```

   Edite o arquivo `.env` para guardar a configuração local, mas mantenha as variáveis definidas no terminal antes de executar o Django. O projeto não lê arquivos `.env` automaticamente.

   Edite o `.env`:

   | Variável | Descrição | Exemplo local |
   |---|---|---|
   | `SECRET_KEY` | Chave usada pelo Django. Gere uma chave exclusiva com o comando acima e mantenha-a fora do repositório. | `django-insecure-<valor-gerado-localmente>` |
   | `DEBUG` | Ativa o modo de desenvolvimento. | `True` |
   | `ALLOWED_HOSTS` | Hosts aceitos pelo Django, separados por vírgula. | `localhost,127.0.0.1` |
   | `DATABASE_URL` | URL de conexão com o PostgreSQL local. | `postgresql://conecta:conecta@localhost:5432/conectasocial` |

5. Crie o banco PostgreSQL local, aplique as migrations e carregue os dados de desenvolvimento:

   ```bash
   psql -U postgres -c "CREATE DATABASE conectasocial;"
   python manage.py migrate
   python manage.py seed
   ```

   As migrations em `core/migrations/` são a fonte oficial da estrutura do banco. O comando `seed` pode ser executado novamente sem duplicar os dados. A aplicação também possui fallback para `db.sqlite3` quando `DATABASE_URL` não está definida, mas o fluxo documentado usa PostgreSQL.

6. Suba o servidor:

   ```bash
   python manage.py runserver
   ```

7. Acesse `http://127.0.0.1:8000`.

### Alternativa com Docker

Docker é opcional e recomendado para quem não é desenvolvedor ou não quer instalar Python e PostgreSQL separadamente. Ele cria a aplicação e o PostgreSQL em containers, deixando o ambiente igual para toda a equipe.

Pré-requisitos adicionais:

- Docker Engine 24+
- Docker Compose v2+

Suba os serviços:

```bash
docker compose up --build
```

O mesmo comando funciona no PowerShell e no `cmd.exe`. No Windows, abra o Docker Desktop antes de executá-lo.

O container web executa automaticamente `migrate` e `seed` antes de iniciar o servidor. Acesse `http://127.0.0.1:8000`.

Comandos úteis:

```bash
docker compose exec web python manage.py test
docker compose exec web python manage.py check
docker compose down
```

Para apagar também os dados persistidos do PostgreSQL local:

```bash
docker compose down -v
```

O deploy atual continua usando o ambiente Python nativo configurado em `render.yaml`. O `Dockerfile` fica disponível para uma futura mudança do Render para deploy por container.

## Estrutura do repositório

```text
/conecta/             — configurações do projeto Django
/core/                — aplicação Django e views principais
/templates/           — templates HTML da aplicação
/static/              — CSS e arquivos estáticos
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
requirements.txt      — dependências Python
render.yaml           — configuração de deploy no Render
```

## Convenções da equipe

- Branches: `feature/nome-da-feature`, `fix/nome-do-problema` e `docs/nome-do-documento`, sempre criadas a partir de `main`.
- Commits: Conventional Commits, no formato `<tipo>(escopo-opcional): <descrição>`.
- Tipos aceitos: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style` e `test`.
- Exemplos: `feat: adiciona cadastro de doador` e `fix(auth): corrige login do administrador`.
- Toda PR exige revisão de pelo menos 1 integrante antes do merge na `main`.

## Testes

Execute os testes e a checagem do Django com o ambiente virtual ativado:

```bash
python manage.py check
python manage.py test
```

Para verificar se há alterações nos models sem migration correspondente:

```bash
python manage.py makemigrations --check
```

Para instalar os hooks executados antes dos commits:

```bash
pre-commit install
pre-commit install --hook-type commit-msg
```

O CI em [`.github/workflows/ci.yml`](.github/workflows/ci.yml) executa Ruff, `manage.py check`, os testes Django e a validação das mensagens de commit em pull requests e pushes para `main`.

## Protótipo navegável

O protótipo navegável está disponível no [Figma](https://www.figma.com/proto/TyUOya1fWIhDOESS57yEqy/Conecta-Social?node-id=1669-162202&t=Ic0Ttr16nL0o8TLl-1). O roteiro completo está em [`docs/prototipo.md`](docs/prototipo.md).

## Licença / Uso acadêmico

Projeto desenvolvido para a disciplina de Laboratório de Engenharia de Software — ADS, Fatec Ribeirão Preto, 2026.
