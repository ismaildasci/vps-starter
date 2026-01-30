# Memory High - Runbook

## Alert: YuksekBellek / KritikBellek

### Severity
- **Warning (YuksekBellek)**: Memory > 75% for 5 minutes
- **Critical (KritikBellek)**: Memory > 90% for 2 minutes

### Symptoms
- Slow response times
- OOM (Out of Memory) kills
- Swap usage increasing
- Applications crashing

### Diagnosis Steps

1. **Check current memory usage**
```bash
free -h
cat /proc/meminfo | head -10
```

2. **Identify top memory consumers**
```bash
ps aux --sort=-%mem | head -15
```

3. **Check Docker container memory**
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.MemPerc}}"
```

4. **Check swap usage**
```bash
swapon --show
vmstat 1 5
```

5. **Check for memory leaks**
```bash
# Check process memory over time
watch -n 5 'ps aux --sort=-%mem | head -10'
```

### Resolution Steps

#### If a container is consuming high memory:

1. **Identify the container**
```bash
docker stats --no-stream | sort -k4 -h -r | head -10
```

2. **Check container logs for errors**
```bash
docker logs <container_name> --tail 100
```

3. **Restart the container**
```bash
docker restart <container_name>
```

4. **If memory limits are not set, add them**
```yaml
services:
  app:
    mem_limit: 512m
    mem_reservation: 256m
```

#### If system is low on memory:

1. **Clear system caches (safe)**
```bash
sync; echo 3 > /proc/sys/vm/drop_caches
```

2. **Check for zombie processes**
```bash
ps aux | awk '$8=="Z"'
```

3. **Restart non-critical services**
```bash
docker restart <non-critical-container>
```

4. **Add more swap if needed**
```bash
sudo fallocate -l 2G /swapfile2
sudo chmod 600 /swapfile2
sudo mkswap /swapfile2
sudo swapon /swapfile2
```

### Prevention

1. Set container memory limits:
```yaml
services:
  app:
    mem_limit: 512m
    mem_reservation: 256m
```

2. Configure Redis maxmemory:
```bash
redis-server --maxmemory 256mb --maxmemory-policy allkeys-lru
```

3. Monitor memory trends in Grafana
4. Set up proper swap space (2x RAM or 2GB, whichever is smaller)

### Emergency Actions

If system is unresponsive:

1. **SSH into server** (if possible)
2. **Kill largest process**
```bash
# Find and kill largest memory consumer
kill -9 $(ps aux | sort -k4 -rn | head -1 | awk '{print $2}')
```

3. **Restart Docker**
```bash
sudo systemctl restart docker
```

### Escalation

If memory remains high after basic remediation:
1. Contact on-call engineer
2. Consider vertical scaling (add RAM)
3. Review application for memory leaks
4. Check for DDoS or unusual traffic

### Related Alerts
- ContainerYuksekBellek
- ContainerOOMKilled
- RedisKritikBellek

### Dashboard
[Grafana Memory Dashboard](https://grafana-dev.yourdomain.com/d/vps-overview)
