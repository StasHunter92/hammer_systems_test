FROM python:3.10-slim

WORKDIR /hammer_systems

ENV PYTHONUNBUFFERED=1

RUN pip install poetry

COPY pyproject.toml .
COPY poetry.lock .
COPY apps/. ./apps
COPY config/. ./config
COPY .env .

COPY manage.py .

RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-root

EXPOSE 8000
# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]