FROM python:3.11-slim

WORKDIR /app

# Copia apenas dependências primeiro (melhor cache)
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante da aplicação
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
