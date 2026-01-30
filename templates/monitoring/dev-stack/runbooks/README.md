# Runbooks

Incident response procedures for VPS monitoring alerts.

## Available Runbooks

| Runbook | Alerts Covered | Severity |
|---------|----------------|----------|
| [CPU High](cpu-high.md) | YuksekCPU, KritikCPU | Warning, Critical |
| [Memory High](memory-high.md) | YuksekBellek, KritikBellek | Warning, Critical |
| [Disk Low](disk-low.md) | DusukDisk, KritikDisk | Warning, Critical |
| [Container Down](container-down.md) | ContainerDown, ContainerRestartLoop | Critical, Warning |
| [Website Down](website-down.md) | WebsiteDown, WebsiteYavash | Critical, Warning |
| [PostgreSQL & Redis](postgres-redis.md) | PostgreSQLDown, RedisDown, etc. | Critical, Warning |

## Quick Reference

### Emergency Commands

```bash
# Check all container status
docker ps -a

# Check system resources
free -h && df -h && top -bn1 | head -20

# Restart a container
docker restart <container_name>

# View container logs
docker logs <container_name> --tail 100

# Full stack restart
cd /home/deploy/apps/<project> && docker compose restart
```

### Severity Levels

| Level | Response Time | Action |
|-------|---------------|--------|
| Critical | Immediate | Page on-call, investigate immediately |
| Warning | 30 minutes | Investigate, may require action |
| Info | Next business day | Review during maintenance window |

## On-Call Procedures

1. **Acknowledge** the alert via Telegram `/ack <hash>`
2. **Investigate** using the appropriate runbook
3. **Resolve** or **Escalate** as needed
4. **Document** actions taken

## Useful Links

- [Grafana Dashboards](https://grafana-dev.yourdomain.com)
- [Prometheus Alerts](https://prometheus-dev.yourdomain.com/alerts)
- [Alertmanager](https://alerts-dev.yourdomain.com)
