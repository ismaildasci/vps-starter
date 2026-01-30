#!/bin/bash

# Initialize Traefik with Cloudflare certificate
# Run as deploy user: bash 09-traefik-init.sh yourdomain.com

set -e

DOMAIN="${1:-yourdomain.com}"
TRAEFIK_DIR="$HOME/traefik"

if [ -z "$1" ]; then
    echo "Usage: bash $0 yourdomain.com"
    exit 1
fi

echo "=========================================="
echo "Traefik Setup for $DOMAIN"
echo "=========================================="

# Create directories
mkdir -p "$TRAEFIK_DIR/certs"
cd "$TRAEFIK_DIR"

# traefik.yml
cat > traefik.yml << 'EOF'
api:
  dashboard: false
  insecure: false

entryPoints:
  web:
    address: ":80"
  websecure:
    address: ":443"

providers:
  docker:
    endpoint: "unix:///var/run/docker.sock"
    exposedByDefault: false
    network: web
  file:
    filename: /dynamic.yml
    watch: true

log:
  level: INFO

accessLog: {}
EOF

# dynamic.yml
cat > dynamic.yml << EOF
tls:
  certificates:
    - certFile: /certs/${DOMAIN}.crt
      keyFile: /certs/${DOMAIN}.key
EOF

# docker-compose.yml
cat > docker-compose.yml << 'EOF'
services:
  traefik:
    image: traefik:latest
    container_name: traefik
    restart: unless-stopped
    security_opt:
      - no-new-privileges:true
    environment:
      - DOCKER_API_VERSION=1.44
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/localtime:/etc/localtime:ro
      - /var/run/docker.sock:/var/run/docker.sock:ro
      - ./traefik.yml:/traefik.yml:ro
      - ./dynamic.yml:/dynamic.yml:ro
      - ./certs:/certs:ro
    networks:
      - web

networks:
  web:
    external: true
EOF

echo ""
echo "Traefik files created in $TRAEFIK_DIR"
echo ""
echo "Next steps:"
echo "1. Go to Cloudflare → SSL/TLS → Origin Server"
echo "2. Create certificate for: $DOMAIN, *.$DOMAIN"
echo "3. Save certificate to: $TRAEFIK_DIR/certs/${DOMAIN}.crt"
echo "4. Save private key to: $TRAEFIK_DIR/certs/${DOMAIN}.key"
echo "5. Set Cloudflare SSL mode to 'Full'"
echo "6. Start Traefik: cd ~/traefik && docker compose up -d"
