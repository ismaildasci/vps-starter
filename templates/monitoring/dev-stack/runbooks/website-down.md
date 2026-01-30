# Website Down - Runbook

## Alert: WebsiteDown / WebsiteYavash

### Severity
- **Critical (WebsiteDown)**: Website not responding for 2 minutes
- **Warning (WebsiteYavash)**: Response time > 3 seconds for 5 minutes

### Symptoms
- Website returning 5xx errors
- Connection timeouts
- SSL certificate errors
- DNS resolution failures

### Diagnosis Steps

1. **Quick check from server**
```bash
curl -I https://your-domain.com
curl -w "@-" -o /dev/null -s "https://your-domain.com" <<'EOF'
    time_namelookup:  %{time_namelookup}s
    time_connect:     %{time_connect}s
    time_appconnect:  %{time_appconnect}s
    time_pretransfer: %{time_pretransfer}s
    time_redirect:    %{time_redirect}s
    time_starttransfer: %{time_starttransfer}s
    time_total:       %{time_total}s
EOF
```

2. **Check Traefik status**
```bash
docker ps | grep traefik
docker logs traefik --tail 50
```

3. **Check Traefik routing**
```bash
# Access Traefik API
curl http://localhost:8080/api/http/routers
```

4. **Check backend container**
```bash
docker ps -a | grep <app-name>
docker logs <app-container> --tail 100
```

5. **Check SSL certificate**
```bash
# Check certificate expiry
echo | openssl s_client -servername your-domain.com -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

6. **Check DNS**
```bash
dig your-domain.com
nslookup your-domain.com
```

### Resolution Steps

#### If Traefik is down:

```bash
# Restart Traefik
cd /home/deploy/traefik
docker compose restart traefik

# Check logs
docker logs traefik --tail 100
```

#### If backend container is down:

```bash
# Restart the application
cd /home/deploy/apps/<project>
docker compose up -d

# Check health
docker compose ps
```

#### If SSL certificate expired:

```bash
# Force certificate renewal
docker exec traefik sh -c "rm -rf /letsencrypt/acme.json"
docker restart traefik

# Or if using Cloudflare
# Check Cloudflare dashboard for certificate status
```

#### If DNS is not resolving:

1. Check Cloudflare/DNS provider dashboard
2. Verify A record points to correct IP
3. Wait for DNS propagation (up to 24h)

#### If high latency:

```bash
# Check container resources
docker stats --no-stream

# Check database connection
docker logs <db-container> --tail 50

# Check for slow queries (if applicable)
```

### Common Issues

#### 502 Bad Gateway
- Backend container not running
- Backend health check failing
- Wrong port configuration

```bash
# Fix: Restart backend
docker restart <backend-container>

# Check port in docker-compose.yml matches Traefik label
```

#### 503 Service Unavailable
- No healthy backend
- Circuit breaker open

```bash
# Fix: Restart all app containers
docker compose restart
```

#### 504 Gateway Timeout
- Backend taking too long
- Database connection issues

```bash
# Fix: Check database, restart app
docker restart <db-container>
docker restart <app-container>
```

#### SSL/TLS Errors
- Certificate expired
- Certificate not matching domain

```bash
# Fix: Renew certificate
docker exec traefik touch /letsencrypt/acme.json
docker restart traefik
```

### Prevention

1. **Set up proper health checks** in docker-compose.yml
2. **Monitor SSL certificate expiry** via Blackbox exporter
3. **Set up uptime monitoring** via Uptime Kuma
4. **Configure proper timeouts** in Traefik

### Quick Recovery Commands

```bash
# Full stack restart (nuclear option)
cd /home/deploy/apps/<project>
docker compose down
docker compose up -d

# Traefik restart
cd /home/deploy/traefik
docker compose restart

# Check all services
docker ps --format "table {{.Names}}\t{{.Status}}"
```

### Escalation

If website remains down:
1. Check CloudFlare/CDN status
2. Check hosting provider status
3. Contact on-call engineer
4. Consider switching to maintenance page

```bash
# Enable maintenance mode via Traefik
# Update dynamic.yml to route to maintenance container
```

### Related Alerts
- TraefikDown
- ContainerDown
- SSLSertifikasiKritik

### Dashboard
[Grafana Website Dashboard](https://grafana-dev.yourdomain.com/d/website-uptime)
