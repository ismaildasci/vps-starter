#!/bin/bash

# Create deploy user with sudo access
# Run as root: sudo bash 01-user.sh

set -e

USERNAME="${1:-deploy}"

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

echo "Creating user: $USERNAME"

# Create user
if id "$USERNAME" &>/dev/null; then
    echo "User $USERNAME already exists"
else
    adduser --disabled-password --gecos "" "$USERNAME"
    echo "User $USERNAME created"
fi

# Add to sudo group (passwordless)
echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME
chmod 440 /etc/sudoers.d/$USERNAME
echo "Sudo access granted"

# Create SSH directory
mkdir -p /home/$USERNAME/.ssh
chmod 700 /home/$USERNAME/.ssh
touch /home/$USERNAME/.ssh/authorized_keys
chmod 600 /home/$USERNAME/.ssh/authorized_keys
chown -R $USERNAME:$USERNAME /home/$USERNAME/.ssh

# Create directory structure
sudo -u $USERNAME mkdir -p /home/$USERNAME/{apps,traefik,shared,envs,backups,scripts,logs}
echo "Directory structure created"

echo ""
echo "Done! Next steps:"
echo "1. Add your SSH public key to /home/$USERNAME/.ssh/authorized_keys"
echo "2. Test SSH login: ssh $USERNAME@$(hostname -I | awk '{print $1}')"
echo "3. Run: sudo bash 02-packages.sh"
