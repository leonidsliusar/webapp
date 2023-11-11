FROM python:3.11-alpine
LABEL authors="leo"
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install --upgrade pip
RUN pip install poetry
COPY pyproject.toml /app/pyproject.toml
RUN poetry config virtualenvs.create false
RUN poetry install --no-interaction --no-dev
RUN poetry update
COPY ./app /app
CMD python main.py
