# Use Python 3.11 slim image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p data ExcelFiles

# Set environment variables
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Expose the port that Cloud Run will use
EXPOSE 8080

# Install gunicorn for production
RUN pip install gunicorn==21.2.0

# Start command
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]