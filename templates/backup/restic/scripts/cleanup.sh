#!/bin/bash
# Restic Cleanup Script
# Removes old snapshots based on retention policy

set -euo pipefail

# Retention policy (customize as needed)
KEEP_LAST="${KEEP_LAST:-7}"
KEEP_DAILY="${KEEP_DAILY:-7}"
KEEP_WEEKLY="${KEEP_WEEKLY:-4}"
KEEP_MONTHLY="${KEEP_MONTHLY:-6}"
KEEP_YEARLY="${KEEP_YEARLY:-2}"

log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Main
main() {
    log "=========================================="
    log "Restic Cleanup Starting"
    log "=========================================="
    log "Retention policy:"
    log "  Keep last: $KEEP_LAST"
    log "  Keep daily: $KEEP_DAILY"
    log "  Keep weekly: $KEEP_WEEKLY"
    log "  Keep monthly: $KEEP_MONTHLY"
    log "  Keep yearly: $KEEP_YEARLY"
    log "=========================================="

    # Show current snapshots
    log "Current snapshots:"
    restic snapshots

    # Apply retention policy
    log "Applying retention policy..."
    restic forget \
        --keep-last "$KEEP_LAST" \
        --keep-daily "$KEEP_DAILY" \
        --keep-weekly "$KEEP_WEEKLY" \
        --keep-monthly "$KEEP_MONTHLY" \
        --keep-yearly "$KEEP_YEARLY" \
        --prune

    # Check repository integrity
    log "Checking repository integrity..."
    restic check

    # Show remaining snapshots
    log "Remaining snapshots:"
    restic snapshots

    # Show stats
    log "Repository stats:"
    restic stats

    log "=========================================="
    log "Cleanup finished"
    log "=========================================="
}

main "$@"
