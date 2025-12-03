FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./

RUN npm install

COPY . .

# Garante permissão de execução nos scripts
RUN chmod +x ./node_modules/.bin/* || true

RUN npm run build