FROM python:3.11-slim

WORKDIR /app

# Install system dependencies including PostgreSQL client libraries and Redis client
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    postgresql-client \
    redis-tools \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code and scripts
COPY . /app

# Set Python path to include /app
ENV PYTHONPATH=/app

CMD [ "bash", "scripts/start_sync.sh" ]