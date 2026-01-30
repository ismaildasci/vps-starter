#!/bin/bash

# SSH Hardening
# Run as root: sudo bash 06-ssh-hardening.sh
# WARNING: Make sure you have SSH key access before running!

set -e

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

echo "=========================================="
echo "WARNING: SSH Hardening"
echo "=========================================="
echo ""
echo "This will:"
echo "  - Disable root login"
echo "  - Disable password authentication"
echo ""
echo "Make sure you have SSH key access first!"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

echo "Creating SSH hardening config..."

cat > /etc/ssh/sshd_config.d/hardening.conf << 'EOF'
# SSH Hardening

# Disable root login
PermitRootLogin no

# Disable password authentication
PasswordAuthentication no
ChallengeResponseAuthentication no

# Only allow key-based auth
PubkeyAuthentication yes
AuthenticationMethods publickey

# Disable empty passwords
PermitEmptyPasswords no

# Disable X11 forwarding
X11Forwarding no

# Timeout settings
ClientAliveInterval 300
ClientAliveCountMax 2

# Limit authentication attempts
MaxAuthTries 3
MaxSessions 5

# Disable unused authentication methods
HostbasedAuthentication no
IgnoreRhosts yes
EOF

echo "Testing SSH configuration..."
sshd -t

if [ $? -eq 0 ]; then
    echo "Configuration valid. Restarting SSH..."
    systemctl restart sshd
    echo ""
    echo "SSH hardened successfully!"
else
    echo "Configuration error! Removing hardening config..."
    rm /etc/ssh/sshd_config.d/hardening.conf
    exit 1
fi

echo ""
echo "Setup complete! Run: sudo bash 07-verify.sh"
