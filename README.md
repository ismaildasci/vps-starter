# VPS Starter

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-24.0+-blue.svg)](https://www.docker.com/)
[![Traefik](https://img.shields.io/badge/Traefik-v3-24a1c1.svg)](https://traefik.io/)

Production-ready VPS setup. Docker, Traefik, SSL, monitoring, security. One script, done.

## Architecture

```
                                    ┌─────────────────────────────────────────────────────────┐
                                    │                        VPS                              │
                                    │                                                         │
┌──────────┐      ┌─────────┐       │   ┌─────────────────────────────────────────────────┐   │
│          │      │         │       │   │                   Traefik                       │   │
│ Internet │─────▶│Cloudflare│──────┼──▶│  - SSL termination (Cloudflare DNS challenge)  │   │
│          │      │   DNS   │       │   │  - Rate limiting, security headers             │   │
└──────────┘      └─────────┘       │   │  - Automatic service discovery                 │   │
                                    │   └──────────────────────┬──────────────────────────┘   │
                                    │                          │                              │
                                    │            ┌─────────────┼─────────────┐               │
                                    │            │             │             │               │
                                    │            ▼             ▼             ▼               │
                                    │   ┌─────────────┐ ┌───────────┐ ┌───────────┐         │
                                    │   │   Nuxt     │ │  Laravel  │ │   Go      │         │
                                    │   │   Next.js  │ │  NestJS   │ │   API     │         │
                                    │   │   React    │ │           │ │           │         │
                                    │   └─────────────┘ └─────┬─────┘ └───────────┘         │
                                    │                         │                              │
                                    │                         ▼                              │
                                    │            ┌────────────────────────┐                  │
                                    │            │   MySQL │ PostgreSQL  │                  │
                                    │            │   Redis │              │                  │
                                    │            └────────────────────────┘                  │
                                    │                                                         │
                                    │   ┌─────────────────────────────────────────────────┐   │
                                    │   │              Monitoring Stack                   │   │
                                    │   │  Prometheus → Grafana → Alertmanager           │   │
                                    │   │  Loki → Promtail (logs)                         │   │
                                    │   │  Homer │ Portainer │ Uptime Kuma               │   │
                                    │   └─────────────────────────────────────────────────┘   │
                                    │                                                         │
                                    │   ┌─────────────────────────────────────────────────┐   │
                                    │   │              Security Layer                     │   │
                                    │   │  UFW │ Fail2ban │ CrowdSec │ SSH Hardening     │   │
                                    │   └─────────────────────────────────────────────────┘   │
                                    │                                                         │
                                    └─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
# Fresh Ubuntu 22.04+ VPS (as root)
git clone https://github.com/ismaildasci/vps-starter.git
cd vps-starter/scripts/setup
sudo bash setup.sh deploy 2
```

Installs Docker, UFW, Fail2ban, swap, aliases. Creates `deploy` user with 2GB swap.

## What You Get

| Component | What it does |
|-----------|--------------|
| Docker + Compose | Container runtime |
| UFW | Firewall (22, 80, 443 only) |
| Fail2ban | Blocks brute force attacks |
| SSH Hardening | Key-only, no root login |
| Swap | Configurable (default 2GB) |
| Aliases | `dps`, `dcup`, `dclogs`... |

## Templates

### Frontend
| Template | Stack |
|----------|-------|
| Nuxt | Nuxt 4, Vue 3 |
| Next.js | Next 14+, React |
| React | Vite, nginx |
| Vue | Vite, nginx |

### Backend
| Template | Stack |
|----------|-------|
| Laravel | PHP-FPM, nginx |
| NestJS | TypeScript |
| Go | Go 1.22 |

### Database
| Template | Version |
|----------|---------|
| MySQL | 8.0 |
| PostgreSQL | 16 |
| Redis | 7 |

### Monitoring
| Template | Purpose |
|----------|---------|
| Grafana + Prometheus | Metrics & dashboards |
| Loki + Promtail | Log aggregation |
| Homer | Dashboard |
| Portainer | Docker UI |
| Uptime Kuma | Uptime monitoring |

### Security
| Template | Purpose |
|----------|---------|
| CrowdSec | Modern IPS with Traefik bouncer |

## Project Structure

```
├── scripts/
│   ├── setup/           # Server setup (run once)
│   ├── backup.sh        # Volume backups
│   ├── restore.sh       # Restore backups
│   └── env-*.sh         # Env management + GPG
│
├── config/              # Server configs
│   ├── fail2ban/
│   ├── ssh/
│   └── docker/
│
├── templates/           # Copy & deploy
│   ├── traefik/
│   ├── frontend/
│   ├── backend/
│   ├── databases/
│   ├── monitoring/
│   └── security/
│
└── docs/                # Guides
```

## After Setup (Server Layout)

```
/home/deploy/
├── apps/        # Your projects go here
├── traefik/     # Reverse proxy
├── shared/      # MySQL, Redis (shared)
├── envs/        # .env files (chmod 600)
├── backups/     # Encrypted backups
└── scripts/     # Utilities
```

## Container Hardening

All templates include:
- Memory/CPU limits
- `no-new-privileges` security option
- Health checks
- Read-only filesystem (where possible)
- Non-root users

## Docs

- [Server Setup](docs/01-server-setup.md)
- [Docker Setup](docs/02-docker-setup.md)
- [Traefik Setup](docs/03-traefik-setup.md)
- [Deploy Nuxt](docs/04-deploy-nuxt.md)
- [Deploy Laravel](docs/05-deploy-laravel.md)
- [Monitoring](docs/06-monitoring.md)
- [Security](docs/07-security.md)
- [Troubleshooting](docs/troubleshooting.md)

## Aliases

After setup, you get these shortcuts:

```bash
dps       # docker ps (formatted)
dcup      # docker compose up -d
dcdown    # docker compose down
dclogs    # docker compose logs -f
dprune    # cleanup unused stuff
apps      # cd ~/apps
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md)

## License

[MIT](LICENSE)
