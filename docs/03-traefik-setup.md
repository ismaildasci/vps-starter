# Traefik Setup

Configure Traefik v3 as reverse proxy with Cloudflare SSL.

## 1. Directory Structure

```bash
mkdir -p ~/traefik/certs
cd ~/traefik
```

## 2. Create Configuration Files

### traefik.yml (Static Configuration)

```yaml
api:
  dashboard: false
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: web
  file:
    filename: /dynamic.yml
    watch: true

log:
  level: INFO

accessLog: {}
```

### dynamic.yml (Dynamic Configuration)

```yaml
tls:
  certificates:
    - certFile: /certs/yourdomain.com.crt
      keyFile: /certs/yourdomain.com.key
```

### docker-compose.yml

```yaml
services:
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    environment:
      - DOCKER_API_VERSION=1.44
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./dynamic.yml:/dynamic.yml:ro
      - ./certs:/certs:ro
    networks:
      - web

networks:
  web:
    external: true
```

## 3. Cloudflare SSL Certificate

1. Go to Cloudflare Dashboard → SSL/TLS → Origin Server
2. Create Certificate (select your domain + wildcard *.yourdomain.com)
3. Save certificate as `certs/yourdomain.com.crt`
4. Save private key as `certs/yourdomain.com.key`
5. Set SSL/TLS mode to **Full**

## 4. Start Traefik

```bash
docker compose up -d
docker logs traefik -f
```

## 5. Verify

```bash
# Check if Traefik is running
docker ps | grep traefik

# Test routing (should return 404 - no backends yet)
curl -I http://localhost
```

## Troubleshooting

### Docker API Version Error
If you see "client version X is too old", add environment variable:
```yaml
environment:
  - DOCKER_API_VERSION=1.44
```

## Next Steps

→ [Deploy Nuxt](04-deploy-nuxt.md)
