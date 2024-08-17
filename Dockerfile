# Use uma imagem Python como base
FROM python:3.12-slim

# Defina o diretório de trabalho
WORKDIR /app

# Copie o requirements.txt e instale as dependências
COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copie todo o código para o diretório de trabalho
COPY . .

# Comando para executar o script Python
CMD ["python3", "main.py"]
