FROM python:3.12-slim

# Install curl (needed for uv install)
RUN apt-get update && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.local/bin:$PATH"

# Set working directory
WORKDIR /app

# Copy dependency files first (better Docker caching)
COPY pyproject.toml uv.lock ./

# Install dependencies (production only)
RUN uv sync --no-dev

# Copy project files
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Run using FastAPI CLI
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

# 2 CPU → 2 workers
# 4 CPU → 4 workers