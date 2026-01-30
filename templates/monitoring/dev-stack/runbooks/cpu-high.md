# CPU High - Runbook

## Alert: YuksekCPU / KritikCPU

### Severity
- **Warning (YuksekCPU)**: CPU > 70% for 5 minutes
- **Critical (KritikCPU)**: CPU > 90% for 2 minutes

### Symptoms
- Slow response times
- High load average
- Process queuing

### Diagnosis Steps

1. **Check current CPU usage**
```bash
top -bn1 | head -20
htop  # if available
```

2. **Identify top CPU consumers**
```bash
ps aux --sort=-%cpu | head -15
```

3. **Check Docker containers**
```bash
docker stats --no-stream --format "table {{.Name}}\t{{.CPUPerc}}\t{{.MemUsage}}"
```

4. **Check load average**
```bash
uptime
cat /proc/loadavg
```

5. **Check for runaway processes**
```bash
# Processes using >50% CPU
ps aux | awk '$3 > 50'
```

### Resolution Steps

#### If a container is consuming high CPU:

1. **Identify the container**
```bash
docker stats --no-stream
```

2. **Check container logs**
```bash
docker logs <container_name> --tail 100
```

3. **Restart the container (if safe)**
```bash
docker restart <container_name>
```

4. **If persistent, check for memory leaks or infinite loops**
```bash
docker exec -it <container_name> top
```

#### If system processes are consuming CPU:

1. **Check for cron jobs**
```bash
cat /var/log/syslog | grep CRON | tail -20
```

2. **Check for package updates**
```bash
ps aux | grep -E "(apt|dpkg|unattended)"
```

3. **Kill runaway process (last resort)**
```bash
kill -15 <PID>  # Graceful
kill -9 <PID>   # Force (last resort)
```

### Prevention

1. Set container CPU limits in docker-compose.yml:
```yaml
services:
  app:
    cpus: 1.0
    mem_limit: 512m
```

2. Monitor CPU trends in Grafana
3. Set up auto-scaling if applicable
4. Review application performance regularly

### Escalation

If CPU remains high after 30 minutes:
1. Contact on-call engineer
2. Consider horizontal scaling
3. Review application code for optimization

### Related Alerts
- ContainerYuksekCPU
- YuksekLoad

### Dashboard
[Grafana CPU Dashboard](https://grafana-dev.yourdomain.com/d/vps-overview)
