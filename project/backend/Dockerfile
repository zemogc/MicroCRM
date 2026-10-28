FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY app ./app

RUN useradd --create-home microcrm
USER microcrm

EXPOSE 8000

# SEED_DEMO_DATA=true carga los datos de demo antes de iniciar (no duplica si ya existen)
CMD ["sh", "-c", "if [ \"$SEED_DEMO_DATA\" = \"true\" ]; then python -m app.seed; fi && exec uvicorn app.main:app --host 0.0.0.0 --port 8000"]
