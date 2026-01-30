#!/bin/bash

# Docker Volume Backup Script
# Usage: ./backup.sh [container_name] [volume_name]
# Example: ./backup.sh mysql mysql_data

set -e

BACKUP_DIR="${BACKUP_DIR:-$HOME/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-7}"
DATE=$(date +%Y%m%d_%H%M%S)

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
    exit 1
}

# Create backup directory
mkdir -p "$BACKUP_DIR"

backup_volume() {
    local container=$1
    local volume=$2
    local backup_file="$BACKUP_DIR/${container}_${volume}_${DATE}.tar.gz"

    log "Backing up $volume from $container..."

    docker run --rm \
        -v "${volume}:/source:ro" \
        -v "$BACKUP_DIR:/backup" \
        alpine tar czf "/backup/$(basename $backup_file)" -C /source .

    log "Backup created: $backup_file"
}

backup_mysql() {
    local container=${1:-mysql}
    local backup_file="$BACKUP_DIR/${container}_dump_${DATE}.sql.gz"

    log "Creating MySQL dump from $container..."

    docker exec "$container" mysqldump -u root -p"$MYSQL_ROOT_PASSWORD" --all-databases | gzip > "$backup_file"

    log "MySQL dump created: $backup_file"
}

cleanup_old() {
    log "Cleaning up backups older than $RETENTION_DAYS days..."
    find "$BACKUP_DIR" -name "*.tar.gz" -mtime +$RETENTION_DAYS -delete
    find "$BACKUP_DIR" -name "*.sql.gz" -mtime +$RETENTION_DAYS -delete
    log "Cleanup complete"
}

# Main
case "${1:-}" in
    mysql)
        backup_mysql "${2:-mysql}"
        ;;
    volume)
        [ -z "$2" ] || [ -z "$3" ] && error "Usage: $0 volume <container> <volume_name>"
        backup_volume "$2" "$3"
        ;;
    cleanup)
        cleanup_old
        ;;
    all)
        # Backup all named volumes
        for volume in $(docker volume ls -q | grep -v "^[a-f0-9]\{64\}$"); do
            backup_volume "docker" "$volume"
        done
        cleanup_old
        ;;
    *)
        echo "Usage: $0 {mysql|volume|cleanup|all}"
        echo ""
        echo "Commands:"
        echo "  mysql [container]     - Backup MySQL database"
        echo "  volume <cont> <vol>   - Backup specific volume"
        echo "  cleanup               - Remove old backups"
        echo "  all                   - Backup all named volumes"
        exit 1
        ;;
esac

log "Done!"
