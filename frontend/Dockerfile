FROM node:22-alpine

WORKDIR /app

COPY package.json /app/package.json
RUN npm install

COPY . /app

CMD ["sh", "-c", "npm install && npm run dev -- --host 0.0.0.0"]
