# Базовый образ с общими системными зависимостями для dev и prod
FROM python:3.11.3-slim as python-base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONFAULTHANDLER=1 \
    PYTHONPATH="/opt:$PYTHONPATH" \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PYSETUP_PATH="/opt/pysetup" \
    VENV_PATH="/opt/pysetup/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# Библиотеки, необходимые в процессе работы сервиса
#RUN apt-get update \
#    && apt-get --no-install-recommends install -y \
#    тут список библиотек
#    && rm -rf /var/lib/apt/lists/*

# Билдер для установки Python пакетов и необходимых системных зависимостей
FROM python-base as builder
# Программы и библиотеки для сборки и установки зависимостей
RUN apt-get update \
    && apt-get --no-install-recommends install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry в папку POETRY_HOME с учетом версии
SHELL ["/bin/bash", "-o", "pipefail", "-c"]
RUN curl -sSL https://install.python-poetry.org | POETRY_VERSION=1.4.2 python3 -

# Установка Python пакетов для продакшена
WORKDIR $PYSETUP_PATH
COPY ./poetry.lock ./pyproject.toml ./
RUN poetry install --only main --no-root

# development образ
FROM python-base as development

# Копируем Poetry и Python пакеты для продакшена из билдера
COPY --from=builder $POETRY_HOME $POETRY_HOME
COPY --from=builder $PYSETUP_PATH $PYSETUP_PATH

# Устанавливаем остальные Python пакеты
WORKDIR $PYSETUP_PATH
RUN poetry install --no-root

WORKDIR /opt/app/
COPY ./app .

EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# 'production' образ
FROM python-base as production

# Копируем только Python пакеты (без Poetry)
COPY --from=builder $VENV_PATH $VENV_PATH

WORKDIR /opt/app
COPY ./app .

RUN groupadd -r app && useradd -d /opt/app -r -g app app \
    && chown app:app -R /opt/app
USER app

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "main:app"]
