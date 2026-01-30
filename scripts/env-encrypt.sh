#!/bin/bash

# Encrypt all .env files with GPG
# Usage: ./env-encrypt.sh [passphrase]

set -e

ENV_DIR="${ENV_DIR:-$HOME/envs}"
BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
DATE=$(date +%Y%m%d_%H%M%S)
OUTPUT="$BACKUP_DIR/envs_${DATE}.tar.gz.gpg"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[encrypt]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }

# Check if env files exist
if [ ! -d "$ENV_DIR" ] || [ -z "$(ls -A $ENV_DIR/*.env 2>/dev/null)" ]; then
    warn "No .env files found in $ENV_DIR"
    exit 1
fi

mkdir -p "$BACKUP_DIR"

log "Encrypting env files from $ENV_DIR..."

# Create tar and encrypt with GPG
if [ -n "$1" ]; then
    # Use provided passphrase
    tar czf - -C "$ENV_DIR" . | gpg --batch --yes --passphrase "$1" -c -o "$OUTPUT"
else
    # Interactive passphrase
    tar czf - -C "$ENV_DIR" . | gpg -c -o "$OUTPUT"
fi

chmod 600 "$OUTPUT"

log "Encrypted backup: $OUTPUT"
log "Size: $(du -h "$OUTPUT" | cut -f1)"

# Keep only last 5 encrypted backups
cd "$BACKUP_DIR"
ls -t envs_*.tar.gz.gpg 2>/dev/null | tail -n +6 | xargs -r rm -f

log "Done!"
