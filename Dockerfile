FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Default run: execute the included test runner
CMD ["/bin/bash", "run_test.sh"]
