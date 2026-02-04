#!/bin/bash
# Restic Backup Script
# Backs up Docker volumes with optional container stopping

set -euo pipefail

# Configuration
VOLUMES_PATH="/volumes"
BACKUP_TAG="${BACKUP_TAG:-docker-volumes}"
STOP_CONTAINERS="${STOP_CONTAINERS:-false}"
CONTAINERS_TO_STOP="${CONTAINERS_TO_STOP:-}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Stop containers if configured
stop_containers() {
    if [ "$STOP_CONTAINERS" = "true" ] && [ -n "$CONTAINERS_TO_STOP" ]; then
        log "Stopping containers: $CONTAINERS_TO_STOP"
        for container in $CONTAINERS_TO_STOP; do
            docker stop "$container" 2>/dev/null || true
        done
        sleep 5
    fi
}

# Start containers back
start_containers() {
    if [ "$STOP_CONTAINERS" = "true" ] && [ -n "$CONTAINERS_TO_STOP" ]; then
        log "Starting containers: $CONTAINERS_TO_STOP"
        for container in $CONTAINERS_TO_STOP; do
            docker start "$container" 2>/dev/null || true
        done
    fi
}

# Initialize repository if needed
init_repo() {
    if ! restic snapshots &>/dev/null; then
        log "Initializing restic repository..."
        restic init
    fi
}

# Run backup
run_backup() {
    log "Starting backup..."

    # Exclude patterns
    local exclude_opts=""
    exclude_opts="$exclude_opts --exclude='*.tmp'"
    exclude_opts="$exclude_opts --exclude='*.log'"
    exclude_opts="$exclude_opts --exclude='*.cache'"
    exclude_opts="$exclude_opts --exclude='*/.git'"

    # Run restic backup
    restic backup \
        --tag "$BACKUP_TAG" \
        --tag "$(date +%Y-%m-%d)" \
        $exclude_opts \
        "$VOLUMES_PATH"

    log "Backup completed successfully"
}

# Main
main() {
    log "=========================================="
    log "Restic Backup Starting"
    log "Repository: $RESTIC_REPOSITORY"
    log "=========================================="

    # Trap to ensure containers are restarted on error
    trap start_containers EXIT

    init_repo
    stop_containers
    run_backup
    start_containers

    # Show stats
    log "Recent snapshots:"
    restic snapshots --last 5

    log "=========================================="
    log "Backup finished"
    log "=========================================="
}

main "$@"
