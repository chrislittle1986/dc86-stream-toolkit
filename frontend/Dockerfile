FROM node:20-alpine

WORKDIR /app

# Dependencies installieren
COPY package.json package-lock.json* ./
RUN npm install

# App-Code
COPY . .

# Vite Dev-Server starten (Hot-Reload)
EXPOSE 5173
CMD ["npm", "run", "dev", "--", "--host", "0.0.0.0"]
