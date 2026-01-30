#!/bin/bash

# Verify server setup
# Run as: bash 07-verify.sh

set -e

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

ok() { echo -e "${GREEN}✓${NC} $1"; }
fail() { echo -e "${RED}✗${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }

echo "=========================================="
echo "Server Setup Verification"
echo "=========================================="
echo ""

# User
echo "== User =="
id deploy &>/dev/null && ok "deploy user exists" || fail "deploy user missing"
groups deploy | grep -q docker && ok "deploy in docker group" || fail "deploy not in docker group"
[ -f /etc/sudoers.d/deploy ] && ok "sudo configured" || fail "sudo not configured"
echo ""

# Docker
echo "== Docker =="
command -v docker &>/dev/null && ok "Docker installed: $(docker --version | cut -d' ' -f3)" || fail "Docker not installed"
command -v docker &>/dev/null && docker compose version &>/dev/null && ok "Docker Compose installed" || fail "Docker Compose not installed"
docker network ls | grep -q web && ok "Network 'web' exists" || fail "Network 'web' missing"
systemctl is-active docker &>/dev/null && ok "Docker running" || fail "Docker not running"
echo ""

# Firewall
echo "== Firewall =="
systemctl is-active ufw &>/dev/null && ok "UFW active" || warn "UFW not active"
ufw status | grep -q "22/tcp" && ok "SSH port open" || warn "SSH port not configured"
ufw status | grep -q "80/tcp" && ok "HTTP port open" || warn "HTTP port not open"
ufw status | grep -q "443/tcp" && ok "HTTPS port open" || warn "HTTPS port not open"
echo ""

# Fail2ban
echo "== Fail2ban =="
systemctl is-active fail2ban &>/dev/null && ok "Fail2ban active" || warn "Fail2ban not active"
[ -f /etc/fail2ban/jail.local ] && ok "jail.local configured" || warn "jail.local missing"
echo ""

# SSH
echo "== SSH =="
[ -f /etc/ssh/sshd_config.d/hardening.conf ] && ok "SSH hardening applied" || warn "SSH hardening not applied"
grep -q "PermitRootLogin no" /etc/ssh/sshd_config.d/hardening.conf 2>/dev/null && ok "Root login disabled" || warn "Root login may be enabled"
grep -q "PasswordAuthentication no" /etc/ssh/sshd_config.d/hardening.conf 2>/dev/null && ok "Password auth disabled" || warn "Password auth may be enabled"
echo ""

# Directories
echo "== Directories =="
[ -d /home/deploy/apps ] && ok "~/apps exists" || fail "~/apps missing"
[ -d /home/deploy/traefik ] && ok "~/traefik exists" || fail "~/traefik missing"
[ -d /home/deploy/envs ] && ok "~/envs exists" || fail "~/envs missing"
[ -d /home/deploy/backups ] && ok "~/backups exists" || fail "~/backups missing"
echo ""

echo "=========================================="
echo "Verification complete!"
echo "=========================================="
