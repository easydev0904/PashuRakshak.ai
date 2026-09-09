# Build context is the REPO ROOT (see docker-compose.yml), so this
# Dockerfile can also copy infra/docker/nginx.conf without reaching
# outside its build context.

FROM node:20-slim AS build

WORKDIR /app

COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

COPY frontend/ .

# Vite bakes VITE_* env vars in at build time. docker-compose.yml passes
# the backend's docker-network address as a build arg by default.
ARG VITE_API_BASE_URL=http://localhost:8000/api/v1
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL

RUN npm run build

FROM nginx:1.27-alpine AS serve

COPY --from=build /app/dist /usr/share/nginx/html
COPY infra/docker/nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
