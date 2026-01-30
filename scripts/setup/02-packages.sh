#!/bin/bash

# Install essential packages
# Run as root: sudo bash 02-packages.sh

set -e

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

echo "Updating system..."
apt-get update
apt-get upgrade -y

echo "Installing essential packages..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    tmux \
    unzip \
    ca-certificates \
    gnupg \
    lsb-release \
    apt-transport-https \
    software-properties-common

echo "Installing security packages..."
apt-get install -y \
    ufw \
    fail2ban \
    unattended-upgrades

echo "Enabling automatic security updates..."
dpkg-reconfigure -plow unattended-upgrades

echo "Cleaning up..."
apt-get autoremove -y
apt-get clean

echo ""
echo "Done! Next: sudo bash 03-docker.sh"
