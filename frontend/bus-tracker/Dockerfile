# Usa uma imagem leve do Node.js (versão 18 ou 20)
FROM node:20-alpine AS builder

# Define a pasta de trabalho dentro do container
WORKDIR /app

# Copia os arquivos de dependências primeiro (para aproveitar o cache do Docker)
COPY package*.json ./

# Instala as dependências
RUN npm install

# Copia o restante do código do projeto para dentro do container
COPY . .

# Build the application
RUN npm run build