# Stage 1: Builder
FROM python:3.14.3-slim-bookworm AS builder
LABEL authors="simonmichau"

# Install uv directly
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Install system build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libssl-dev \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Use distinct name for the build directory to avoid issues with the stage 2 workdir
WORKDIR /abc

# Set environment variables
ENV UV_COMPILE_BYTECODE=1
ENV UV_LINK_MODE=copy

# Copy only the dependency files first
COPY pyproject.toml uv.lock ./

# Install dependencies
RUN uv sync --frozen --no-install-project --no-dev

# Copy the actual application code
COPY . .

# Final sync to install the project itself
RUN uv sync --frozen --no-dev

# Stage 2: Final
FROM python:3.14.3-slim-bookworm

WORKDIR /app

# Copy everything from the builder
COPY --from=builder /abc /app

# Ensure the data directory exists
RUN mkdir -p /app/data

# Streamlit environment variables
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0
# Set the path so the container knows where our python lives
ENV PATH="/app/.venv/bin:$PATH"

EXPOSE 8501

# Execute using the specific python interpreter in the venv
# This avoids "command not found" and "Failed to spawn" errors
CMD ["python", "-m", "streamlit", "run", "app.py"]

# Deploayment notes:
# docker build -t unit-ball .
# docker run -v ./local_data:/app/data -p 8501:8501 unit-ball