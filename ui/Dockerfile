FROM python:3.12-slim

WORKDIR /app

# Copiar requirements (o instalar directamente)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY streamlit_app.py .

# Exponer puerto
EXPOSE 8501

# Comando
CMD ["streamlit", "run", "streamlit_app.py", "--server.address=0.0.0.0", "--server.port=8501"]
