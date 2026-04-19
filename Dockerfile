FROM python:3.11-slim

# Evita travar instalação
ENV DEBIAN_FRONTEND=noninteractive

# 🔥 Instalar dependências nativas (ESSENCIAL)
RUN apt-get update && apt-get install -y \
    build-essential \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    proj-bin \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

# Diretório da app
WORKDIR /app

# Copiar requirements primeiro (cache otimizado)
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar resto do projeto
COPY . .

# Porta do Streamlit
EXPOSE 8501

# Rodar app
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
