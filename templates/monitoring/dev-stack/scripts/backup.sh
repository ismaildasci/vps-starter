#!/bin/bash
# VPS Backup Script
# Daily backup with retention and Telegram notification

set -e

# Configuration
BACKUP_DIR="${BACKUP_DIR:-/home/deploy/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-}"
TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID:-}"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() { echo -e "${GREEN}[$(date +%H:%M:%S)]${NC} $1"; }
error() { echo -e "${RED}[ERROR]${NC} $1"; }

send_telegram() {
    if [ -n "$TELEGRAM_BOT_TOKEN" ] && [ -n "$TELEGRAM_CHAT_ID" ]; then
        curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
            -d chat_id="$TELEGRAM_CHAT_ID" \
            -d text="$1" \
            -d parse_mode="HTML" > /dev/null
    fi
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

log "Starting backup..."

# Backup Docker volumes
backup_volumes() {
    log "Backing up Docker volumes..."

    VOLUMES=$(docker volume ls -q)
    for vol in $VOLUMES; do
        if [[ "$vol" != *"_tmp"* ]]; then
            log "  - $vol"
            docker run --rm \
                -v "$vol":/source:ro \
                -v "$BACKUP_DIR":/backup \
                alpine tar czf "/backup/vol_${vol}_${DATE}.tar.gz" -C /source . 2>/dev/null || true
        fi
    done
}

# Backup database (PostgreSQL)
backup_postgres() {
    local container=$1
    local db_name=$2
    local db_user=$3

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log "Backing up PostgreSQL: $container"
        docker exec "$container" pg_dump -U "$db_user" "$db_name" | \
            gzip > "$BACKUP_DIR/pg_${container}_${DATE}.sql.gz"
    fi
}

# Backup Redis
backup_redis() {
    local container=$1

    if docker ps --format '{{.Names}}' | grep -q "^${container}$"; then
        log "Backing up Redis: $container"
        docker exec "$container" redis-cli BGSAVE > /dev/null
        sleep 2
        docker cp "$container":/data/dump.rdb "$BACKUP_DIR/redis_${container}_${DATE}.rdb" 2>/dev/null || true
    fi
}

# Backup Traefik config
backup_traefik() {
    if [ -d "/home/deploy/traefik" ]; then
        log "Backing up Traefik config..."
        tar czf "$BACKUP_DIR/traefik_${DATE}.tar.gz" -C /home/deploy traefik
    fi
}

# Cleanup old backups
cleanup() {
    log "Cleaning up backups older than ${RETENTION_DAYS} days..."
    find "$BACKUP_DIR" -type f -mtime +$RETENTION_DAYS -delete
}

# Main
backup_volumes
backup_traefik

# Backup known databases (customize as needed)
# backup_postgres "app-postgres" "app_db" "app_user"
# backup_redis "app-redis"

cleanup

# Calculate total size
TOTAL_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
BACKUP_COUNT=$(find "$BACKUP_DIR" -type f -name "*_${DATE}*" | wc -l)

log "Backup complete!"
log "Files: $BACKUP_COUNT, Total size: $TOTAL_SIZE"

# Send notification
send_telegram "💾 <b>Backup Complete</b>
📁 Files: $BACKUP_COUNT
📊 Size: $TOTAL_SIZE
📅 Date: $(date +%Y-%m-%d)"
