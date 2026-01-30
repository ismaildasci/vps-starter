#!/bin/bash

# Docker Volume Restore Script
# Usage: ./restore.sh <backup_file> <volume_name>

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

BACKUP_FILE=$1
VOLUME_NAME=$2

[ -z "$BACKUP_FILE" ] && error "Usage: $0 <backup_file> <volume_name>"
[ -z "$VOLUME_NAME" ] && error "Usage: $0 <backup_file> <volume_name>"
[ ! -f "$BACKUP_FILE" ] && error "Backup file not found: $BACKUP_FILE"

warn "This will overwrite all data in volume: $VOLUME_NAME"
read -p "Are you sure? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log "Cancelled"
    exit 0
fi

log "Restoring $BACKUP_FILE to $VOLUME_NAME..."

# Create volume if not exists
docker volume create "$VOLUME_NAME" 2>/dev/null || true

# Restore
docker run --rm \
    -v "$VOLUME_NAME:/target" \
    -v "$(realpath $BACKUP_FILE):/backup.tar.gz:ro" \
    alpine sh -c "rm -rf /target/* && tar xzf /backup.tar.gz -C /target"

log "Restore complete!"
