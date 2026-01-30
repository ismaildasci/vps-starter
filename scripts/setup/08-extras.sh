#!/bin/bash

# Extra configurations: timezone, swap, aliases, cron
# Run as root: sudo bash 08-extras.sh [username] [swap_size_gb]

set -e

USERNAME="${1:-deploy}"
SWAP_SIZE="${2:-2}"

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0 [username] [swap_gb]"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")/config"

echo "=========================================="
echo "Extra Configurations"
echo "=========================================="

# Timezone
echo ""
echo "[1/5] Setting timezone to UTC..."
timedatectl set-timezone UTC
echo "Timezone: $(timedatectl | grep 'Time zone')"

# Swap
echo ""
echo "[2/5] Configuring swap (${SWAP_SIZE}GB)..."
if [ -f /swapfile ]; then
    echo "Swap already exists"
else
    fallocate -l ${SWAP_SIZE}G /swapfile
    chmod 600 /swapfile
    mkswap /swapfile
    swapon /swapfile
    echo '/swapfile none swap sw 0 0' >> /etc/fstab
    # Optimize swap usage
    echo 'vm.swappiness=10' >> /etc/sysctl.conf
    echo 'vm.vfs_cache_pressure=50' >> /etc/sysctl.conf
    sysctl -p
    echo "Swap configured: ${SWAP_SIZE}GB"
fi

# Bash aliases
echo ""
echo "[3/5] Installing bash aliases..."
if [ -f "$CONFIG_DIR/bash/.bash_aliases" ]; then
    cp "$CONFIG_DIR/bash/.bash_aliases" /home/$USERNAME/.bash_aliases
    chown $USERNAME:$USERNAME /home/$USERNAME/.bash_aliases

    # Add to .bashrc if not exists
    if ! grep -q "bash_aliases" /home/$USERNAME/.bashrc; then
        echo '' >> /home/$USERNAME/.bashrc
        echo '# Load aliases' >> /home/$USERNAME/.bashrc
        echo 'if [ -f ~/.bash_aliases ]; then . ~/.bash_aliases; fi' >> /home/$USERNAME/.bashrc
    fi
    echo "Aliases installed"
else
    echo "Alias file not found, skipping"
fi

# Cron jobs
echo ""
echo "[4/5] Setting up maintenance cron jobs..."
cat > /etc/cron.d/docker-maintenance << EOF
# Docker cleanup - every Sunday at 3am
0 3 * * 0 root docker system prune -af > /dev/null 2>&1

# Docker volume cleanup - every Sunday at 3:30am
30 3 * * 0 root docker volume prune -f > /dev/null 2>&1
EOF

cat > /etc/cron.d/system-maintenance << EOF
# Clear old logs - every day at 4am
0 4 * * * root find /var/log -name "*.gz" -mtime +7 -delete > /dev/null 2>&1

# Update package lists - every day at 5am
0 5 * * * root apt-get update > /dev/null 2>&1
EOF
echo "Cron jobs configured"

# Git config
echo ""
echo "[5/5] Basic git config..."
sudo -u $USERNAME git config --global init.defaultBranch main
sudo -u $USERNAME git config --global pull.rebase false
echo "Git configured"

echo ""
echo "=========================================="
echo "Extras configured!"
echo "=========================================="
echo ""
echo "Swap: ${SWAP_SIZE}GB"
echo "Timezone: UTC"
echo "Aliases: ~/.bash_aliases"
echo "Cron: Docker & system maintenance"
echo ""
echo "Reload shell: source ~/.bashrc"
