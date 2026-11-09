FROM python:3.12.16-slim-bookworm AS base
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app
COPY requirements.lock ./
RUN pip install --no-cache-dir -r requirements.lock
COPY app ./app
COPY migrations ./migrations
COPY alembic.ini ./
RUN groupadd --gid 10001 jg && useradd --create-home --uid 10001 --gid 10001 jg
USER 10001:10001
EXPOSE 8000
CMD ["python", "-m", "app.deploy"]

# Etapa opcional para ejecutar Pytest dentro del mismo servicio api.
FROM base AS test
USER root
COPY requirements-dev.lock ./
RUN pip install --no-cache-dir -r requirements-dev.lock
COPY tests ./tests
COPY pyproject.toml ./
USER 10001:10001

FROM base AS runtime
