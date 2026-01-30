# Disk Low - Runbook

## Alert: DusukDisk / KritikDisk

### Severity
- **Warning (DusukDisk)**: Disk free < 25%
- **Critical (KritikDisk)**: Disk free < 10%

### Symptoms
- Applications failing to write
- Database errors
- Log rotation failures
- Container failures

### Diagnosis Steps

1. **Check disk usage**
```bash
df -h
```

2. **Find largest directories**
```bash
du -sh /* 2>/dev/null | sort -hr | head -10
du -sh /home/deploy/* 2>/dev/null | sort -hr | head -10
```

3. **Check Docker disk usage**
```bash
docker system df
docker system df -v | head -30
```

4. **Find large files**
```bash
find / -type f -size +100M 2>/dev/null | head -20
```

5. **Check log sizes**
```bash
du -sh /var/log/*
ls -lhS /var/log/*.log | head -10
```

### Resolution Steps

#### 1. Clean Docker resources

```bash
# Remove unused containers, networks, images, and volumes
docker system prune -af

# Remove all unused volumes (CAUTION: data loss possible)
docker volume prune -f

# Remove dangling images
docker image prune -f

# Remove old container logs
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

#### 2. Clean system logs

```bash
# Clear old journals (keep last 3 days)
sudo journalctl --vacuum-time=3d

# Rotate logs
sudo logrotate -f /etc/logrotate.conf

# Clear apt cache
sudo apt clean
sudo apt autoclean
```

#### 3. Clean old backups

```bash
# List backups
ls -lh /home/deploy/backups/

# Remove backups older than 7 days
find /home/deploy/backups/ -mtime +7 -delete
```

#### 4. Clean application caches

```bash
# Laravel cache
docker exec <laravel-container> php artisan cache:clear
docker exec <laravel-container> php artisan view:clear

# NPM cache
rm -rf /home/deploy/apps/**/node_modules/.cache
```

#### 5. Remove old Docker images

```bash
# List all images sorted by size
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | sort -k3 -h

# Remove specific old images
docker rmi <image_id>
```

### Prevention

1. **Set up log rotation** in docker-compose.yml:
```yaml
services:
  app:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

2. **Schedule regular cleanups** via cron:
```bash
# Weekly Docker cleanup
0 3 * * 0 docker system prune -af >> /var/log/docker-cleanup.log 2>&1

# Daily backup cleanup (keep 7 days)
0 4 * * * find /home/deploy/backups/ -mtime +7 -delete
```

3. **Monitor disk trends** in Grafana

4. **Set up disk alerts** at 70% and 85%

### Emergency Actions

If disk is 100% full:

1. **Remove large files immediately**
```bash
# Truncate large logs
truncate -s 0 /var/log/syslog
truncate -s 0 /var/lib/docker/containers/*/*-json.log
```

2. **Stop non-critical containers**
```bash
docker stop <non-critical-container>
```

3. **Remove oldest backups**
```bash
ls -lt /home/deploy/backups/ | tail -5 | awk '{print $NF}' | xargs rm -rf
```

### Escalation

If disk cannot be freed:
1. Contact on-call engineer
2. Consider adding more storage
3. Move backups to external storage
4. Review data retention policies

### Related Alerts
- ContainerDown (due to disk full)
- PostgreSQLDown (due to disk full)

### Dashboard
[Grafana Disk Dashboard](https://grafana-dev.yourdomain.com/d/vps-overview)
