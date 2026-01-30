# Troubleshooting Guide

Common issues and solutions.

## Docker Issues

### Docker API Version Error

**Error**: `client version X is too old`

**Solution**: Add environment variable to docker-compose:
```yaml
services:
  traefik:
    environment:
      - DOCKER_API_VERSION=1.44
```

### Container Not Starting

```bash
# Check logs
docker logs container-name

# Check container status
docker ps -a

# Inspect container
docker inspect container-name
```

### Out of Disk Space

```bash
# Check disk usage
df -h

# Clean Docker resources
docker system prune -af
docker volume prune -f

# Remove old images
docker image prune -a
```

## Traefik Issues

### 404 Not Found

**Causes**:
- Container not on `web` network
- `traefik.enable=true` label missing
- Wrong host rule

**Solution**:
```bash
# Check container is on web network
docker network inspect web

# Check container labels
docker inspect container-name | grep -A 50 Labels
```

### SSL Certificate Not Working

**Causes**:
- Certificate files not mounted
- Wrong file permissions
- Certificate/key mismatch

**Solution**:
```bash
# Check certificate files exist
ls -la ~/traefik/certs/

# Verify certificate
openssl x509 -in ~/traefik/certs/yourdomain.com.crt -text -noout

# Check Traefik logs
docker logs traefik | grep -i cert
```

### Service Not Accessible

```bash
# Check Traefik is routing correctly
docker logs traefik -f

# Test from server
curl -H "Host: yourdomain.com" http://localhost

# Check DNS
nslookup yourdomain.com
```

## Laravel Issues

### HTTPS Redirect Loop

**Cause**: Laravel doesn't know it's behind HTTPS proxy

**Solution**: Add to `docker/nginx.conf`:
```nginx
location ~ \.php$ {
    # ... other settings
    fastcgi_param HTTPS on;
}
```

And in `.env`:
```
TRUSTED_PROXIES=*
```

### Vite Build Error: Ziggy Not Found

**Cause**: Ziggy package needs vendor directory during build

**Solution**: In Dockerfile, copy vendor to node stage:
```dockerfile
# Node stage
FROM node:22-alpine AS node-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY resources/ ./resources/
COPY vite.config.ts tsconfig.json tailwind.config.js postcss.config.js ./
COPY --from=composer /app/vendor ./vendor  # Add this line
RUN npm run build
```

### Composer Error: Class Not Found

**Cause**: Artisan scripts running during composer install

**Solution**: Add `--no-scripts` flag:
```dockerfile
RUN composer install --no-dev --no-scripts --no-autoloader --ignore-platform-reqs
RUN composer dump-autoload --optimize --no-dev --no-scripts
```

### Health Check Failing

**IPv6 Connection Refused**:
```yaml
# Use 127.0.0.1 instead of localhost
healthcheck:
  test: ["CMD", "wget", "-qO-", "http://127.0.0.1/up"]
```

**302 Redirect on Health Check**:
```yaml
# Use /up endpoint that returns 200
healthcheck:
  test: ["CMD", "wget", "-qO-", "http://127.0.0.1/up"]
```

### Storage/Uploads Not Working

**Cause**: Storage symlink not created or wrong path

**Solution**: In Dockerfile:
```dockerfile
RUN rm -f public/storage && \
    ln -s /var/www/html/storage/app/public public/storage && \
    chown -R www-data:www-data storage
```

### Permission Denied Errors

```bash
# Fix storage permissions
docker exec container-name chown -R www-data:www-data storage bootstrap/cache
docker exec container-name chmod -R 775 storage bootstrap/cache
```

## Nuxt Issues

### Build Failing

```bash
# Check Node version matches
node --version

# Clear cache and rebuild
rm -rf node_modules .nuxt .output
npm ci
npm run build
```

### Port Already in Use

**Error**: `EADDRINUSE: address already in use`

**Solution**: Check and kill process:
```bash
lsof -i :3000
kill -9 PID
```

## Network Issues

### Container Can't Reach External Services

```bash
# Test from inside container
docker exec container-name ping 8.8.8.8
docker exec container-name curl -v https://api.example.com
```

### DNS Resolution Failing Inside Container

Add to docker-compose:
```yaml
services:
  app:
    dns:
      - 8.8.8.8
      - 8.8.4.4
```

## Monitoring Issues

### Uptime Kuma Shows Down But Site Works

**Causes**:
- Wrong URL in monitor
- Monitor checking from wrong network
- Authentication required

**Solutions**:
- For internal services, use container name: `http://container-name:port`
- For external checks, use full URL: `https://yourdomain.com`
- Add authentication headers if needed

## Useful Debug Commands

```bash
# View all containers
docker ps -a

# View container logs
docker logs container-name -f --tail 100

# Enter container shell
docker exec -it container-name sh

# Check container resource usage
docker stats

# View Docker networks
docker network ls
docker network inspect web

# Check disk usage
docker system df

# View Traefik routing
docker logs traefik 2>&1 | grep -i router
```

## Getting Help

1. Check container logs first
2. Verify network connectivity
3. Confirm DNS is resolving
4. Check Cloudflare SSL settings
5. Review Traefik configuration

If issues persist, check:
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [Docker Documentation](https://docs.docker.com/)
- [Laravel Documentation](https://laravel.com/docs)
- [Nuxt Documentation](https://nuxt.com/docs)
