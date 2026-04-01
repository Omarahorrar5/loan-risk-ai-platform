FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir --timeout=600 -r requirements.txt

COPY ml/ ./ml/

EXPOSE 8000

WORKDIR /app/ml
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]