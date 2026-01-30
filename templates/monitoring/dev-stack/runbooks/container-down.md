# Container Down - Runbook

## Alert: ContainerDown / ContainerRestartLoop

### Severity
- **Critical (ContainerDown)**: Critical container not responding for 1 minute
- **Warning (ContainerRestartLoop)**: Container restarted >3 times in 1 hour

### Symptoms
- Service unavailable
- Health check failures
- 502/503 errors from Traefik

### Diagnosis Steps

1. **Check container status**
```bash
docker ps -a
docker ps -a --filter "status=exited"
```

2. **Check specific container**
```bash
docker inspect <container_name> | grep -A 10 "State"
```

3. **Check container logs**
```bash
docker logs <container_name> --tail 100
docker logs <container_name> --since 10m
```

4. **Check restart count**
```bash
docker inspect <container_name> --format='{{.RestartCount}}'
```

5. **Check resource usage**
```bash
docker stats --no-stream
```

6. **Check Docker events**
```bash
docker events --since 10m --until now --filter container=<container_name>
```

### Resolution Steps

#### 1. Restart the container

```bash
docker restart <container_name>
```

#### 2. If restart fails, check logs for errors

```bash
# Check last 200 lines before crash
docker logs <container_name> --tail 200 2>&1 | less

# Common error patterns
docker logs <container_name> 2>&1 | grep -i "error\|exception\|fatal\|killed"
```

#### 3. Check if dependencies are running

```bash
# For app containers, check database
docker ps | grep -E "(postgres|redis|mysql)"

# Test database connectivity
docker exec <app_container> nc -zv <db_container> <port>
```

#### 4. Check for resource constraints

```bash
# Check if OOM killed
dmesg | grep -i "killed process"
journalctl -u docker --since "10 minutes ago" | grep -i oom
```

#### 5. Rebuild if image is corrupted

```bash
cd /home/deploy/apps/<project>
docker compose build --no-cache <service>
docker compose up -d <service>
```

### Common Issues and Solutions

#### Issue: OOM Killed
```bash
# Solution: Increase memory limit
# In docker-compose.yml:
mem_limit: 1g
mem_reservation: 512m
```

#### Issue: Port already in use
```bash
# Find process using port
lsof -i :<port>
netstat -tlnp | grep <port>

# Kill process or change port
```

#### Issue: Volume permissions
```bash
# Fix permissions
sudo chown -R 1000:1000 /path/to/volume
```

#### Issue: Database connection refused
```bash
# Check database container
docker logs <db_container> --tail 50

# Restart database first
docker restart <db_container>
sleep 10
docker restart <app_container>
```

#### Issue: Health check failing
```bash
# Check health check command
docker inspect <container> --format='{{.Config.Healthcheck}}'

# Test health endpoint manually
docker exec <container> curl -f http://localhost:<port>/health
```

### Prevention

1. **Set proper health checks**
```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:80/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 30s
```

2. **Set restart policy**
```yaml
restart: unless-stopped
```

3. **Set resource limits**
```yaml
mem_limit: 512m
mem_reservation: 256m
cpus: 0.5
```

4. **Configure proper logging**
```yaml
logging:
  driver: "json-file"
  options:
    max-size: "10m"
    max-file: "3"
```

### Escalation

If container keeps crashing:
1. Contact on-call engineer
2. Check recent code deployments
3. Rollback to previous image if needed
4. Review application logs thoroughly

### Related Alerts
- ContainerYuksekCPU
- ContainerYuksekBellek
- ContainerOOMKilled

### Dashboard
[Grafana Docker Dashboard](https://grafana-dev.yourdomain.com/d/docker-host-container)
