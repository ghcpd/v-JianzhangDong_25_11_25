# Dockerfile for Flask Application Security Testing
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    sqlite3 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY input.py .
COPY input_vulnerable.py .

# Create database directory
RUN mkdir -p /app/data

# Set environment variables
ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000
ENV FLASK_DEBUG=False
ENV API_KEY=your-secure-api-key-here

# Expose port
EXPOSE 5000

# Default command runs the secure version
CMD ["python", "input.py"]
