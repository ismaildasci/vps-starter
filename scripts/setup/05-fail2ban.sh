#!/bin/bash

# Configure Fail2ban
# Run as root: sudo bash 05-fail2ban.sh

set -e

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$(dirname "$SCRIPT_DIR")/config"

echo "Configuring Fail2ban..."

# Copy custom config if exists
if [ -f "$CONFIG_DIR/fail2ban/jail.local" ]; then
    cp "$CONFIG_DIR/fail2ban/jail.local" /etc/fail2ban/jail.local
    echo "Custom jail.local copied"
else
    # Create default config
    cat > /etc/fail2ban/jail.local << 'EOF'
[DEFAULT]
bantime = 1h
findtime = 10m
maxretry = 5
ignoreip = 127.0.0.1/8 ::1

[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 24h
EOF
    echo "Default jail.local created"
fi

# Restart fail2ban
systemctl restart fail2ban
systemctl enable fail2ban

echo ""
echo "Fail2ban status:"
fail2ban-client status

echo ""
echo "Done! Next: sudo bash 06-ssh-hardening.sh"
