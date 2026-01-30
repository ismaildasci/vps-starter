# Dev Monitoring Stack

Full observability stack for VPS monitoring.

## Stack

| Service | Description | Port |
|---------|-------------|------|
| Prometheus | Metrics & alerting | 9090 |
| Grafana | Dashboards | 3000 |
| Alertmanager | Alert routing | 9093 |
| Loki | Log aggregation | 3100 |
| Promtail/Alloy | Log collector | - |
| Node Exporter | Host metrics | 9100 |
| cAdvisor | Container metrics | 8080 |
| Blackbox | HTTP/SSL probing | 9115 |
| Telegram Bot | ChatOps alerts | 5001 |
| Homer | Dashboard | 8080 |
| Portainer | Docker UI | 9000 |

## Quick Start

```bash
# Copy env file
cp .env.example .env

# Edit settings
nano .env

# Create networks
docker network create web
docker network create monitoring

# Start
docker compose up -d
```

## Environment Variables

```bash
# Domains
GRAFANA_DOMAIN=grafana.yourdomain.com
PROMETHEUS_DOMAIN=prometheus.yourdomain.com
ALERTMANAGER_DOMAIN=alerts.yourdomain.com

# Grafana
GRAFANA_ADMIN_USER=admin
GRAFANA_ADMIN_PASSWORD=changeme

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your-bot-token
TELEGRAM_CHAT_ID=your-chat-id
```

## Telegram Bot

ChatOps bot for incident management.

### Commands

| Command | Description |
|---------|-------------|
| `/status` | System status |
| `/docker` | Container list |
| `/alerts` | Active alerts |
| `/ack <hash>` | Acknowledge alert |
| `/silence <name> <time>` | Silence alert |
| `/restart <container>` | Restart container |

### Setup

1. Create bot via [@BotFather](https://t.me/botfather)
2. Get chat ID via [@userinfobot](https://t.me/userinfobot)
3. Add to `.env`

## Alert Rules

Included alerts:

- **Host**: CPU, Memory, Disk, Load
- **Container**: Down, Restart loop, OOM
- **Traefik**: HTTP errors, Latency
- **Database**: PostgreSQL, Redis
- **SSL**: Certificate expiry
- **Availability**: Website down

See `prometheus/alerts.yml`

## Runbooks

Incident guides in `runbooks/`:

- [CPU High](runbooks/cpu-high.md)
- [Memory High](runbooks/memory-high.md)
- [Disk Low](runbooks/disk-low.md)
- [Container Down](runbooks/container-down.md)
- [Website Down](runbooks/website-down.md)
- [PostgreSQL & Redis](runbooks/postgres-redis.md)

## Backup

```bash
# Manual
./scripts/backup.sh

# Cron (daily 3am)
0 3 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
```

## Structure

```
dev-stack/
├── docker-compose.yml
├── .env.example
├── prometheus/
│   ├── prometheus.yml
│   └── alerts.yml
├── grafana/provisioning/
├── alertmanager/
├── loki/
├── blackbox/
├── telegram-bot/
├── runbooks/
└── scripts/
```

## Security

All containers include:
- Memory/CPU limits
- `no-new-privileges`
- Health checks
- Non-root users

## Troubleshooting

```bash
# Prometheus targets
curl localhost:9090/api/v1/targets | jq

# Reload Prometheus
curl -X POST localhost:9090/-/reload

# Test Alertmanager
curl -X POST localhost:9093/api/v2/alerts \
  -H "Content-Type: application/json" \
  -d '[{"labels":{"alertname":"test"}}]'
```

## License

MIT
