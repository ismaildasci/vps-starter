#!/bin/bash

# Install Docker and Docker Compose
# Run as root: sudo bash 03-docker.sh [username]

set -e

USERNAME="${1:-deploy}"

if [ "$(id -u)" != "0" ]; then
    echo "Run as root: sudo bash $0"
    exit 1
fi

echo "Removing old Docker versions..."
apt-get remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true

echo "Adding Docker GPG key..."
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "Adding Docker repository..."
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  tee /etc/apt/sources.list.d/docker.list > /dev/null

echo "Installing Docker..."
apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

echo "Adding $USERNAME to docker group..."
usermod -aG docker $USERNAME

echo "Configuring Docker daemon..."
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true
}
EOF

echo "Restarting Docker..."
systemctl restart docker
systemctl enable docker

echo "Creating web network..."
docker network create web 2>/dev/null || echo "Network 'web' already exists"

echo ""
echo "Docker installed!"
docker --version
docker compose version
echo ""
echo "Next: sudo bash 04-firewall.sh"
