# Use Python 3.13.2 as the base image
FROM python:3.13.2-slim

# Install system dependencies as root first
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Create user after system packages are installed
RUN useradd -m -u 1000 user
USER user

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory
WORKDIR $HOME/app

# Copy pyproject.toml and uv.lock first to leverage Docker cache
COPY --chown=user:user pyproject.toml uv.lock ./

# Install Python dependencies using uv
RUN uv sync --frozen --no-dev

# Copy the application code
COPY --chown=user:user . $HOME/app


# Expose the port that Gradio will run on
EXPOSE 7860

# Use uv to run the application with module syntax
CMD ["uv", "run", "python", "-m", "src.gradio_app.app"] 