# Changelog

## [1.0.0] - 2026-01-16

### First Release

#### Security
- Security headers middleware (HSTS, XSS, Clickjacking)
- Rate limiting (100 req/s, strict: 10 req/m for login)
- TLS 1.2+ with modern cipher suites
- CrowdSec IPS with Traefik bouncer
- Container hardening (mem limits, no-new-privileges, healthchecks)
- SSH hardening (key-only, no root)
- Fail2ban + UFW firewall

#### Monitoring
- Prometheus + Node Exporter + cAdvisor
- Grafana dashboards
- Loki + Promtail (logs)
- Alertmanager
- Uptime Kuma, Homer, Portainer

#### Traefik
- Traefik v3 with Docker provider
- Cloudflare DNS challenge SSL
- Gzip/Brotli compression
- Middleware chains

#### Templates
- Frontend: Nuxt, Next.js, React, Vue
- Backend: Laravel, NestJS, Go
- Database: MySQL, PostgreSQL, Redis

#### Scripts
- Full automated server setup (01-09)
- Backup/restore scripts
- GPG env encryption
