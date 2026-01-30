# Monitoring Setup

Set up Uptime Kuma for monitoring with Basic Auth protection.

## 1. Generate Basic Auth Password

```bash
# Using Docker
docker run --rm httpd:alpine htpasswd -nb username 'YourSecurePassword123!' | sed 's/\$/\$\$/g'

# Output example: username:$$apr1$$xxxxx$$yyyyyyyyyyyyyyy
# Save this for the docker-compose file
```

## 2. docker-compose.yml

```yaml
services:
  uptime-kuma:
    image: louislam/uptime-kuma:1
    container_name: uptime-kuma
    restart: unless-stopped
    volumes:
      - data:/app/data
    mem_limit: 256m
    mem_reservation: 128m
    labels:
      - "traefik.enable=true"
      # Router
      - "traefik.http.routers.uptime-kuma.rule=Host(`devops.yourdomain.com`)"
      - "traefik.http.routers.uptime-kuma.entrypoints=websecure"
      - "traefik.http.routers.uptime-kuma.tls=true"
      - "traefik.http.routers.uptime-kuma.middlewares=uptime-kuma-auth"
      # Service
      - "traefik.http.services.uptime-kuma.loadbalancer.server.port=3001"
      # Basic Auth Middleware (replace with your generated hash)
      - "traefik.http.middlewares.uptime-kuma-auth.basicauth.users=username:$$apr1$$xxxxx$$yyyyyyyyyyyyyyy"
    networks:
      - web

volumes:
  data:

networks:
  web:
    external: true
```

## 3. Deploy

```bash
docker compose up -d
```

## 4. DNS Configuration

Add A record in Cloudflare:
- Type: A
- Name: devops
- Content: YOUR_SERVER_IP
- Proxy: ON

## 5. Initial Setup

1. Access `https://devops.yourdomain.com`
2. Enter Basic Auth credentials
3. Create admin account in Uptime Kuma
4. Add monitors for your services

## Recommended Monitors

| Service | URL | Interval |
|---------|-----|----------|
| Main Site | https://yourdomain.com | 60s |
| API | https://api.yourdomain.com/up | 60s |
| Traefik | http://traefik:8080 (internal) | 60s |

## Notification Setup

Uptime Kuma supports:
- Telegram
- Discord
- Slack
- Email (SMTP)
- Webhook
- And many more...

## Next Steps

→ [Security](07-security.md)
