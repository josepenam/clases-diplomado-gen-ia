FROM python:3.12-slim

RUN pip install --no-cache-dir "poetry>=1.8"

RUN poetry config virtualenvs.create false

WORKDIR /code

# Install dependencies first so this layer is cached unless they change.
COPY ./pyproject.toml ./README.md ./poetry.lock* ./
RUN poetry install --no-interaction --no-ansi --no-root

# Then copy the app and install the project itself.
COPY ./app ./app
RUN poetry install --no-interaction --no-ansi

EXPOSE 8080

# fly.io injects $PORT; default to 8080 to match fly.toml's internal_port.
CMD exec uvicorn app.server:app --host 0.0.0.0 --port ${PORT:-8080}
