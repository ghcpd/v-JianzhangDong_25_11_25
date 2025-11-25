FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copy application files
COPY input.py .
COPY secure_input.py .
COPY test_vulnerabilities.py .
COPY report.json .

# Create logs directory
RUN mkdir -p logs

# Set environment variables
ENV FLASK_APP=secure_input.py
ENV PYTHONUNBUFFERED=1
ENV API_KEY=test_key_for_docker

# Run tests
CMD ["python", "-m", "pytest", "test_vulnerabilities.py", "-v", "--tb=short"]
