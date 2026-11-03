FROM node:22.16.0-alpine
WORKDIR /app
COPY package.json ./
COPY server ./server
COPY public ./public
CMD ["node","server/index.mjs"]
