# Estágio 1: compila o CSS (Tailwind + daisyUI) a partir dos templates.
FROM node:20-slim AS css

WORKDIR /app

COPY package.json package-lock.json tailwind.config.js ./
RUN npm ci

COPY static/src ./static/src
COPY templates ./templates
COPY core ./core
RUN npm run build

# Estágio 2: aplicação Django.
FROM python:3.12-slim-trixie

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update \
    && apt-get upgrade -y \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && pip install --no-cache-dir --upgrade "setuptools>=78.1.1" "msgpack>=1.2.1"

COPY . .
COPY --from=css /app/static/css/tailwind.css ./static/css/tailwind.css

RUN python manage.py collectstatic --no-input

EXPOSE 8000

CMD ["gunicorn", "conecta.wsgi:application", "--bind", "0.0.0.0:8000"]