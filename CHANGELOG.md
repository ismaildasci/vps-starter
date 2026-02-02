# Changelog

## [1.1.0] - 2026-02-02

### Zero Trust & AI Release

#### Networking (NEW)
- **Tailscale template**: Zero Trust mesh VPN for private service access
  - Userspace networking mode
  - Subnet router support
  - Exit node capability
- **Cloudflare Tunnel template**: Zero Trust access without exposing ports
  - No firewall ports needed
  - Built-in DDoS protection
  - Access policies support

#### AI / LLM Stack (NEW)
- **Ollama template**: Local LLM runtime
  - CPU and GPU (NVIDIA) support
  - Model persistence
  - OpenAI-compatible API
- **Open WebUI template**: ChatGPT-like interface
  - Built-in authentication
  - RAG support for document chat
  - Multi-model switching
- **n8n template**: AI workflow automation
  - 400+ integrations
  - PostgreSQL backend
  - Webhook support
  - LangChain/Ollama integration

#### Documentation
- Updated README with new template sections
- Added docs for Zero Trust networking
- Added docs for AI/LLM stack setup

---

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
