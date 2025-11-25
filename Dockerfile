FROM python:3.11-slim
WORKDIR /app
COPY . /app
RUN pip install --upgrade pip && pip install -r requirements.txt
ENV API_KEY=DUMMY
ENV SECRET_KEY=dummy_secret
ENV DEBUG=False
EXPOSE 5000
CMD ["python", "input.py"]
