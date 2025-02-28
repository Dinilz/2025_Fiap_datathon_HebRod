# Use uma imagem base oficial do Python
FROM python:3.9-slim

RUN apt-get update && apt-get install -y \
    build-essential \
    libatlas-base-dev \
    liblapack-dev \
    gfortran \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*
    
# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo requirements.txt para dentro do container
COPY requirements.txt /app/

# Instale as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copie apenas os arquivos necessários para o container
COPY 4_API_recomendacao.py /app/
COPY svd_model.pkl /app/
COPY df_news.pkl /app/
COPY df_final_2.pkl /app/

# Exponha a porta em que a API irá rodar
EXPOSE 8000

# Defina o comando para rodar a API
CMD ["uvicorn", "4_API_recomendacao:app", "--host", "0.0.0.0", "--port", "8000"]
