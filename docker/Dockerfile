# --- STAGE 1: Builder ---
FROM python:3.11-slim as builder

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# --- STAGE 2: Runner ---
FROM python:3.11-slim as runner

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Adiciona as pastas de binários e bibliotecas ao caminho do sistema
ENV PATH="/install/bin:${PATH}"
ENV PYTHONPATH="/install/lib/python3.11/site-packages"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /install

RUN addgroup --system django && adduser --system --group django

# Copia o código do projeto
COPY . .

# Ajusta permissões (não precisamos mais de sed para scripts Python)
RUN chown -R django:django /app

USER django

EXPOSE 8000

ENTRYPOINT ["python", "docker/scripts/entrypoint.py"]

CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "3", "config.wsgi:application"]
