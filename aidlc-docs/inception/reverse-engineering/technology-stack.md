# Technology Stack

## Programming Languages
- Python 3.x — backend (Django)
- HTML + Django Template Language — views server-rendered
- Tailwind CSS / DaisyUI (via classes utilitárias nos templates) — estilo

## Frameworks
- Django >=5.2,<6.0 — framework web full-stack (ORM, auth, forms, templates)

## Infrastructure
- PostgreSQL (produção, via `DATABASE_URL`) / SQLite (dev local)
- WhiteNoise — servir arquivos estáticos
- Gunicorn — servidor WSGI de produção

## Build Tools
- pip + `requirements.txt`
- `manage.py` (comandos Django: migrate, runserver, test, etc.)

## Testing Tools
- Django `TestCase` (baseado em `unittest`), `django.test.Client`
- `ruff` — linting
- `pre-commit` — hooks de qualidade antes do commit
