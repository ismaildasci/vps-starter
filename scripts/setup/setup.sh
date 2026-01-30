#!/bin/bash

# Full server setup - run all steps
# Run as root: sudo bash setup.sh [username] [swap_gb]

set -e

USERNAME="${1:-deploy}"
SWAP_GB="${2:-2}"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

if [ "$(id -u)" != "0" ]; then
    echo "Usage: sudo bash $0 [username] [swap_gb]"
    echo "Example: sudo bash $0 deploy 2"
    exit 1
fi

echo "=========================================="
echo "VPS Docker Traefik - Full Setup"
echo "=========================================="
echo ""
echo "Username: $USERNAME"
echo "Swap: ${SWAP_GB}GB"
echo ""
echo "This will install:"
echo "  - Essential packages"
echo "  - Docker & Docker Compose"
echo "  - UFW Firewall"
echo "  - Fail2ban"
echo "  - Shell aliases"
echo "  - Maintenance cron jobs"
echo ""
read -p "Continue? (y/N) " -n 1 -r
echo
[[ ! $REPLY =~ ^[Yy]$ ]] && exit 0

echo ""
echo "======================================="
echo "[1/7] Creating user..."
echo "======================================="
bash "$SCRIPT_DIR/01-user.sh" "$USERNAME"

echo ""
echo "======================================="
echo "[2/7] Installing packages..."
echo "======================================="
bash "$SCRIPT_DIR/02-packages.sh"

echo ""
echo "======================================="
echo "[3/7] Installing Docker..."
echo "======================================="
bash "$SCRIPT_DIR/03-docker.sh" "$USERNAME"

echo ""
echo "======================================="
echo "[4/7] Configuring firewall..."
echo "======================================="
bash "$SCRIPT_DIR/04-firewall.sh"

echo ""
echo "======================================="
echo "[5/7] Configuring Fail2ban..."
echo "======================================="
bash "$SCRIPT_DIR/05-fail2ban.sh"

echo ""
echo "======================================="
echo "[6/7] Extras (swap, aliases, cron)..."
echo "======================================="
bash "$SCRIPT_DIR/08-extras.sh" "$USERNAME" "$SWAP_GB"

echo ""
echo "======================================="
echo "[7/7] Verifying setup..."
echo "======================================="
bash "$SCRIPT_DIR/07-verify.sh"

echo ""
echo "=========================================="
echo "Setup Complete!"
echo "=========================================="
echo ""
echo "IMPORTANT - Still needed:"
echo ""
echo "1. Add SSH public key:"
echo "   echo 'your-public-key' >> /home/$USERNAME/.ssh/authorized_keys"
echo ""
echo "2. Test SSH login (new terminal):"
echo "   ssh $USERNAME@$(hostname -I | awk '{print $1}')"
echo ""
echo "3. After confirming SSH works, harden SSH:"
echo "   sudo bash $SCRIPT_DIR/06-ssh-hardening.sh"
echo ""
echo "4. Setup Traefik:"
echo "   su - $USERNAME"
echo "   bash ~/scripts/setup/09-traefik-init.sh yourdomain.com"
echo ""
