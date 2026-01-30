# VPS Docker Traefik Starter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![Traefik](https://img.shields.io/badge/Traefik-v3-24a1c1.svg)](https://traefik.io/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-22.04+-E95420.svg)](https://ubuntu.com/)

Production-ready VPS setup with Docker, Traefik, and deployment templates.

## Features

- **Automated Setup** - Single script server configuration
- **Traefik v3** - Reverse proxy with Cloudflare SSL
- **Frontend** - Nuxt, Next.js, React, Vue
- **Backend** - Laravel, NestJS, Go
- **Databases** - MySQL, PostgreSQL, Redis
- **Security** - UFW, Fail2ban, CrowdSec, SSH hardening, Container hardening
- **Monitoring** - Homer, Grafana, Prometheus, Portainer, Uptime Kuma
- **Scripts** - Backup, env management, GPG encryption

## Quick Start

```bash
# On fresh Ubuntu 22.04+ VPS (as root)
git clone https://github.com/username/vps-docker-traefik-starter.git
cd vps-docker-traefik-starter/scripts/setup
sudo bash setup.sh deploy 2
```

This installs everything: Docker, firewall, fail2ban, swap, aliases.

## What Gets Installed

| Component | Description |
|-----------|-------------|
| Docker + Compose | Container runtime |
| UFW | Firewall (22, 80, 443) |
| Fail2ban | Brute force protection |
| Swap | 2GB (configurable) |
| Aliases | Docker shortcuts |
| Cron | Auto cleanup jobs |

## Directory Structure

```
├── scripts/
│   ├── setup/              # Server setup scripts
│   │   ├── setup.sh        # Full automated setup
│   │   ├── 01-user.sh      # Create deploy user
│   │   ├── 02-packages.sh  # Install packages
│   │   ├── 03-docker.sh    # Install Docker
│   │   ├── 04-firewall.sh  # Configure UFW
│   │   ├── 05-fail2ban.sh  # Configure Fail2ban
│   │   ├── 06-ssh-hardening.sh
│   │   ├── 07-verify.sh    # Verify setup
│   │   ├── 08-extras.sh    # Swap, aliases, cron
│   │   └── 09-traefik-init.sh
│   ├── backup.sh           # Volume backups
│   ├── restore.sh
│   ├── env-encrypt.sh      # GPG encrypt envs
│   ├── env-decrypt.sh
│   └── env-manager.sh
│
├── config/
│   ├── fail2ban/jail.local
│   ├── ssh/hardening.conf
│   ├── docker/daemon.json
│   └── bash/.bash_aliases
│
├── templates/
│   ├── traefik/
│   ├── frontend/           # nuxt, nextjs, react, vue
│   ├── backend/            # laravel, nestjs, go
│   ├── databases/          # mysql, postgresql, redis
│   ├── monitoring/         # homer, grafana, prometheus, portainer, uptime-kuma, dev-stack
│   └── security/           # crowdsec
│
├── envs/                   # .env file storage
└── docs/                   # Detailed guides
```

## Server Layout (After Setup)

```
/home/deploy/
├── apps/           # Your projects
├── traefik/        # Reverse proxy
├── shared/         # MySQL, Redis
├── envs/           # .env files (chmod 600)
├── backups/        # Encrypted backups
├── scripts/        # Utility scripts
└── logs/
```

## Templates

| Template | Stack | Port |
|----------|-------|------|
| Nuxt | Nuxt 4, Vue 3 | 3000 |
| Next.js | Next.js 14+ | 3000 |
| React | Vite, nginx | 80 |
| Vue | Vite, nginx | 80 |
| Laravel | PHP-FPM, nginx | 80 |
| NestJS | TypeScript | 3000 |
| Go | Go 1.22 | 8080 |
| MySQL | 8.0 | 3306 |
| PostgreSQL | 16 | 5432 |
| Redis | 7 | 6379 |

### Monitoring Stack

| Template | Description | Port |
|----------|-------------|------|
| Homer | Dashboard | 8080 |
| Grafana | Metrics & Dashboards | 3000 |
| Prometheus | Time Series DB | 9090 |
| Portainer | Docker Management | 9000 |
| Uptime Kuma | Status Monitoring | 3001 |
| dev-stack | All-in-one monitoring | - |

### Security

| Template | Description |
|----------|-------------|
| CrowdSec | Modern IPS - Fail2ban alternative with Traefik bouncer |

### Container Hardening (Built-in)

All templates include:
- `mem_limit` / `mem_reservation` - Memory limits
- `cpus` - CPU limits
- `security_opt: no-new-privileges` - Privilege escalation prevention
- `healthcheck` - Container health monitoring
- `read_only` (where applicable) - Read-only root filesystem

## Documentation

- [Server Setup](docs/01-server-setup.md)
- [Docker Setup](docs/02-docker-setup.md)
- [Traefik Setup](docs/03-traefik-setup.md)
- [Deploy Nuxt](docs/04-deploy-nuxt.md)
- [Deploy Laravel](docs/05-deploy-laravel.md)
- [Monitoring](docs/06-monitoring.md)
- [Security](docs/07-security.md)
- [Troubleshooting](docs/troubleshooting.md)

## Useful Aliases (after setup)

```bash
dps          # docker ps (formatted)
dcup         # docker compose up -d
dcdown       # docker compose down
dclogs       # docker compose logs -f
dprune       # cleanup docker
apps         # cd ~/apps
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[MIT](LICENSE)
