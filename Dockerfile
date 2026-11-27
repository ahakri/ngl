FROM node:22-slim AS build
WORKDIR /app
COPY package*.json ./
RUN npm ci --omit=dev
COPY web/package*.json web/
RUN npm --prefix web ci
COPY . .
RUN npm --prefix web run build && rm -rf web/node_modules

FROM node:22-slim
WORKDIR /app
ENV NODE_ENV=production PORT=8080 DATABASE_PATH=/data/siteline.db NODE_NO_WARNINGS=1
COPY --from=build /app /app
VOLUME /data
EXPOSE 8080
CMD ["node", "server/index.js"]
