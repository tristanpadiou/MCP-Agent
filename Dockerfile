# Use Python 3.13.2 slim image for efficiency
FROM python:3.13.2-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Install system dependencies if needed
RUN apt-get update && apt-get install -y \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY agent.py .
COPY app.py .

# Create directories that might be needed
RUN mkdir -p notebooks

# Expose the port that Gradio will run on
EXPOSE 7860

# Set the command to run the application
CMD ["python", "app.py"] 