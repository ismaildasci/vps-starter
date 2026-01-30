#!/bin/bash

# Sync encrypted env backup to remote location
# Usage: ./env-sync.sh <remote> [encrypted_file]
# Example: ./env-sync.sh user@backup-server:~/envs/

set -e

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
REMOTE="$1"
FILE="$2"

GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[sync]${NC} $1"; }

if [ -z "$REMOTE" ]; then
    echo "Usage: $0 <remote_destination> [encrypted_file]"
    echo ""
    echo "Examples:"
    echo "  $0 user@server:~/backups/"
    echo "  $0 s3://bucket/envs/"
    echo "  $0 /mnt/usb/backups/"
    exit 1
fi

# Find latest backup if not specified
if [ -z "$FILE" ]; then
    FILE=$(ls -t "$BACKUP_DIR"/envs_*.tar.gz.gpg 2>/dev/null | head -1)
    [ -z "$FILE" ] && { echo "No encrypted backup found. Run env-encrypt.sh first."; exit 1; }
fi

log "Syncing: $FILE"
log "To: $REMOTE"

# Detect remote type and sync
if [[ "$REMOTE" == s3://* ]]; then
    aws s3 cp "$FILE" "$REMOTE"
elif [[ "$REMOTE" == *:* ]]; then
    scp "$FILE" "$REMOTE"
else
    cp "$FILE" "$REMOTE"
fi

log "Done!"
