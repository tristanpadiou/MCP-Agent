# Use Python 3.13.2 slim image for efficiency
FROM python:3.13.2-slim

# Install system dependencies and uv
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Copy project configuration files first to leverage Docker layer caching
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy application files
COPY src/ ./src/

# Create directories that might be needed
RUN mkdir -p notebooks

# Expose the port that Gradio will run on
EXPOSE 7860

# Use uv to run the application
CMD ["uv", "run", "python", "src/gradio_app/app.py"] 