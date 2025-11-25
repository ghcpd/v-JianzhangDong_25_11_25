FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY input.py .
COPY test_vuln.py .

# Set environment variables for security
ENV FLASK_APP=input.py
ENV FLASK_ENV=production
ENV API_KEY=secure_production_key_change_me
ENV DEFAULT_PASSWORD_HASH=$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5eDVf7/tK5sue

# Expose port 5000
EXPOSE 5000

# Run Flask app
CMD ["python", "-m", "flask", "run", "--host=0.0.0.0"]
