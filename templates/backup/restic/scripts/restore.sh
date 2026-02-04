#!/bin/bash
# Restic Restore Script
# Restores Docker volumes from backup

set -euo pipefail

# Configuration
RESTORE_TARGET="${RESTORE_TARGET:-/tmp/restore}"
SNAPSHOT="${1:-latest}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# List available snapshots
list_snapshots() {
    log "Available snapshots:"
    restic snapshots
}

# Restore specific snapshot
restore_snapshot() {
    local snapshot_id="$1"
    local target="$2"

    log "Restoring snapshot $snapshot_id to $target..."

    mkdir -p "$target"
    restic restore "$snapshot_id" --target "$target"

    log "Restore completed to: $target"
    log "Contents:"
    ls -la "$target"
}

# Restore specific volume
restore_volume() {
    local snapshot_id="$1"
    local volume_name="$2"
    local target="$3"

    log "Restoring volume $volume_name from snapshot $snapshot_id..."

    mkdir -p "$target"
    restic restore "$snapshot_id" \
        --target "$target" \
        --include "/volumes/${volume_name}*"

    log "Volume restored to: $target"
}

# Show help
show_help() {
    cat << EOF
Restic Restore Script

Usage:
    ./restore.sh                    # List all snapshots
    ./restore.sh latest             # Restore latest snapshot
    ./restore.sh abc123             # Restore specific snapshot
    ./restore.sh abc123 volume_name # Restore specific volume

Environment Variables:
    RESTORE_TARGET  - Target directory for restore (default: /tmp/restore)

Examples:
    # List all snapshots
    docker exec restic /scripts/restore.sh

    # Restore latest to /tmp/restore
    docker exec -e RESTORE_TARGET=/tmp/restore restic /scripts/restore.sh latest

    # Restore specific snapshot
    docker exec restic /scripts/restore.sh abc123

    # After restore, copy back to volume
    docker cp restic:/tmp/restore/volumes/myvolume/_data/. /var/lib/docker/volumes/myvolume/_data/

EOF
}

# Main
main() {
    case "${1:-}" in
        "")
            list_snapshots
            ;;
        "-h"|"--help"|"help")
            show_help
            ;;
        *)
            if [ -n "${2:-}" ]; then
                restore_volume "$1" "$2" "$RESTORE_TARGET"
            else
                restore_snapshot "$1" "$RESTORE_TARGET"
            fi
            ;;
    esac
}

main "$@"
