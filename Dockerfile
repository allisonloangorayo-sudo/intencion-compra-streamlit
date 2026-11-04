# Imagen base pequeña que ya trae Python
FROM python:3.12-slim

# Evita archivos .pyc y muestra los logs de inmediato
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Primero las dependencias: si no cambian, Docker reutiliza esta capa en cache
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Luego el código y el modelo ya entrenado (.dockerignore excluye lo que no se necesita)
COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501", "--browser.gatherUsageStats=false"]
