# Dockerfile for testing both vulnerable and secure Flask applications
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY input.py input_secure.py ./
COPY test_vulnerabilities.py ./

# Create logs directory
RUN mkdir -p /app/logs

# Expose Flask port
EXPOSE 5000

# Default command runs tests
CMD ["python", "test_vulnerabilities.py"]
