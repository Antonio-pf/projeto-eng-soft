# Build Instructions

## Prerequisites
- **Build Tool**: pip + Django management commands (não há passo de "build" no sentido de compilação; é uma app Python interpretada)
- **Dependencies**: ver `requirements.txt` (Django, dj-database-url, psycopg, whitenoise, gunicorn; dev: pre-commit, ruff)
- **Environment Variables**: `DATABASE_URL` (opcional — default SQLite local em `db.sqlite3`)
- **System Requirements**: Python 3.12+ (venv já presente em `.venv/`)

## Build Steps

### 1. Instalar dependências
```bash
source .venv/bin/activate
pip install -r requirements.txt
```

### 2. Configurar ambiente
```bash
# Opcional — sem DATABASE_URL, usa SQLite local (db.sqlite3)
export DATABASE_URL=postgres://user:pass@localhost:5432/conecta
```

### 3. Aplicar migrações
```bash
python manage.py migrate
```

### 4. Verificar sucesso
- **Expected Output**: `System check identified no issues (0 silenced).` e `No changes detected` ao rodar `python manage.py makemigrations --check --dry-run`
- **Build Artifacts**: N/A (não há artefato binário; o "build" é o próprio código-fonte + banco migrado)
- **Common Warnings**: `UserWarning: No directory at: .../staticfiles/` durante testes é esperado (WhiteNoise só precisa do diretório em produção, após `collectstatic`)

## Troubleshooting

### Build Fails with Dependency Errors
- **Cause**: versão do Python incompatível ou venv desatualizado
- **Solution**: recriar `.venv` (`python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt`)

### Build Fails with Migration Errors
- **Cause**: model alterado sem migração correspondente
- **Solution**: `python manage.py makemigrations --check --dry-run` para detectar; `python manage.py makemigrations` para gerar
