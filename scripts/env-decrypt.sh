#!/bin/bash

# Decrypt GPG encrypted env backup
# Usage: ./env-decrypt.sh <encrypted_file> [passphrase]

set -e

ENV_DIR="${ENV_DIR:-$HOME/envs}"
ENCRYPTED_FILE="$1"

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[decrypt]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }
error() { echo -e "${RED}[error]${NC} $1" >&2; exit 1; }

if [ -z "$ENCRYPTED_FILE" ]; then
    echo "Usage: $0 <encrypted_file.gpg> [passphrase]"
    echo ""
    echo "Available backups:"
    ls -lh ~/backups/envs_*.tar.gz.gpg 2>/dev/null || echo "  No backups found"
    exit 1
fi

[ ! -f "$ENCRYPTED_FILE" ] && error "File not found: $ENCRYPTED_FILE"

# Confirm overwrite
if [ -d "$ENV_DIR" ] && [ -n "$(ls -A $ENV_DIR/*.env 2>/dev/null)" ]; then
    warn "This will overwrite existing env files in $ENV_DIR"
    read -p "Continue? (y/N) " -n 1 -r
    echo
    [[ ! $REPLY =~ ^[Yy]$ ]] && exit 0
fi

mkdir -p "$ENV_DIR"

log "Decrypting $ENCRYPTED_FILE..."

if [ -n "$2" ]; then
    # Use provided passphrase
    gpg --batch --yes --passphrase "$2" -d "$ENCRYPTED_FILE" | tar xzf - -C "$ENV_DIR"
else
    # Interactive passphrase
    gpg -d "$ENCRYPTED_FILE" | tar xzf - -C "$ENV_DIR"
fi

# Secure permissions
chmod 700 "$ENV_DIR"
chmod 600 "$ENV_DIR"/*.env 2>/dev/null || true

log "Restored to $ENV_DIR"
log "Files:"
ls -la "$ENV_DIR"/*.env 2>/dev/null || echo "  No .env files"

log "Done!"
