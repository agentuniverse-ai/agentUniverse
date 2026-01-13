FROM python:3.10-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==1.7.1

# Copy dependency files first (better layer caching)
COPY pyproject.toml poetry.toml* ./

# Disable virtualenv creation inside container
RUN poetry config virtualenvs.create false

# Install dependencies
RUN poetry install --no-interaction --no-ansi

# Copy project
COPY . .

# Default command: run tests
CMD ["python", "-c", "import agentuniverse; print('agentUniverse environment ready')"]



