#!/bin/bash

# Configure UFW firewall
# Run as root: sudo bash 04-firewall.sh [ssh_port]

set -e

SSH_PORT="${1:-22}"

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

echo "Configuring UFW firewall..."

# Reset UFW
ufw --force reset

# Default policies
ufw default deny incoming
ufw default allow outgoing

# Allow SSH
ufw allow $SSH_PORT/tcp comment 'SSH'

# Allow HTTP/HTTPS for Traefik
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'

# Enable UFW
echo "y" | ufw enable

echo ""
echo "Firewall status:"
ufw status verbose

echo ""
echo "Done! Next: sudo bash 05-fail2ban.sh"
