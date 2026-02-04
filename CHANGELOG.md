# Changelog

## [1.2.0] - 2026-02-04

### Security & Productivity Release

#### Security (NEW)
- **Authelia template**: Single Sign-On (SSO) and Multi-Factor Authentication
  - TOTP and WebAuthn/Passkeys support
  - Native Traefik ForwardAuth integration
  - File-based or LDAP authentication backend
  - Access control policies per domain
  - Brute force protection
  - Redis session storage
- **Vaultwarden template**: Self-hosted Bitwarden-compatible password manager
  - Works with all official Bitwarden clients
  - Admin panel for user management
  - WebSocket live sync support
  - Organizations and sharing
  - Send (secure file/text sharing)
  - ~30MB RAM usage

#### Backup (NEW)
- **Restic template**: Encrypted, deduplicated backups
  - Multiple backend support (S3, B2, local, SFTP)
  - Automatic scheduling with Ofelia
  - Docker volume backup
  - Retention policy management
  - ~50% less storage than plain backups

#### DevOps (NEW)
- **Gitea template**: Lightweight self-hosted Git server
  - GitHub/GitLab alternative
  - Gitea Actions (GitHub Actions compatible CI/CD)
  - Package/Container registry
  - OAuth/OIDC authentication
  - Git LFS support
  - ~100MB RAM usage

#### Productivity (NEW)
- **Stirling PDF template**: Self-hosted PDF manipulation
  - 50+ PDF operations
  - OCR support with multiple languages
  - Privacy-first (no data leaves server)
  - API for automation
  - Convert, merge, split, compress, and more

#### Traefik Enhancements
- Added Authelia ForwardAuth middleware
- New `secure-authelia` middleware chain for SSO-protected services

#### Documentation
- Updated README with new template sections
- Added comprehensive READMEs for each new template

---

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
