# Deploy Nuxt.js Application

Deploy a Nuxt 4 application with Docker and Traefik.

## 1. Project Structure

```
your-nuxt-app/
├── Dockerfile
├── docker-compose.traefik.yml
├── .env
└── ... (your Nuxt app files)
```

## 2. Dockerfile

```dockerfile
# Build stage
FROM node:22-alpine AS builder

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# Production stage
FROM node:22-alpine

WORKDIR /app

COPY --from=builder /app/.output /app/.output

ENV NODE_ENV=production
ENV NUXT_HOST=0.0.0.0
ENV NUXT_PORT=3000

EXPOSE 3000

CMD ["node", ".output/server/index.mjs"]
```

## 3. docker-compose.traefik.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    # Or use pre-built image:
    # image: ghcr.io/username/repo:latest
    container_name: your-app-name
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - NUXT_HOST=0.0.0.0
      - NUXT_PORT=3000
    mem_limit: 512m
    mem_reservation: 128m
    healthcheck:
      test: ["CMD", "wget", "--no-verbose", "--tries=1", "--spider", "http://localhost:3000/"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 15s
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.your-app.rule=Host(`yourdomain.com`) || Host(`www.yourdomain.com`)"
      - "traefik.http.routers.your-app.entrypoints=websecure"
      - "traefik.http.routers.your-app.tls=true"
      - "traefik.http.services.your-app.loadbalancer.server.port=3000"
    networks:
      - web

networks:
  web:
    external: true
```

## 4. Deploy

```bash
# Build and start
docker compose -f docker-compose.traefik.yml build
docker compose -f docker-compose.traefik.yml up -d

# View logs
docker logs your-app-name -f
```

## 5. DNS Configuration

Add A record in Cloudflare:
- Type: A
- Name: @ (or subdomain)
- Content: YOUR_SERVER_IP
- Proxy: ON (orange cloud)

## Next Steps

→ [Deploy Laravel](05-deploy-laravel.md)
