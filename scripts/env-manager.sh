#!/bin/bash

# Environment File Manager
# Manage .env files securely

set -e

ENV_DIR="${ENV_DIR:-$HOME/envs}"
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() { echo -e "${GREEN}[env]${NC} $1"; }
warn() { echo -e "${YELLOW}[warn]${NC} $1"; }

init() {
    mkdir -p "$ENV_DIR"
    chmod 700 "$ENV_DIR"
    log "Initialized env directory: $ENV_DIR"
}

list() {
    echo "Environment files in $ENV_DIR:"
    echo ""
    ls -la "$ENV_DIR"/*.env 2>/dev/null || echo "No .env files found"
}

create() {
    local name=$1
    [ -z "$name" ] && { echo "Usage: $0 create <name>"; exit 1; }

    local file="$ENV_DIR/${name}.env"

    if [ -f "$file" ]; then
        warn "File already exists: $file"
        return 1
    fi

    touch "$file"
    chmod 600 "$file"
    log "Created: $file"
    echo "Edit with: nano $file"
}

link() {
    local env_name=$1
    local target_dir=$2

    [ -z "$env_name" ] || [ -z "$target_dir" ] && {
        echo "Usage: $0 link <env_name> <target_dir>"
        exit 1
    }

    local source="$ENV_DIR/${env_name}.env"
    local target="$target_dir/.env"

    [ ! -f "$source" ] && { echo "Source not found: $source"; exit 1; }
    [ ! -d "$target_dir" ] && { echo "Target dir not found: $target_dir"; exit 1; }

    ln -sf "$source" "$target"
    log "Linked: $source -> $target"
}

copy() {
    local env_name=$1
    local target_dir=$2

    [ -z "$env_name" ] || [ -z "$target_dir" ] && {
        echo "Usage: $0 copy <env_name> <target_dir>"
        exit 1
    }

    local source="$ENV_DIR/${env_name}.env"
    local target="$target_dir/.env"

    [ ! -f "$source" ] && { echo "Source not found: $source"; exit 1; }

    cp "$source" "$target"
    chmod 600 "$target"
    log "Copied: $source -> $target"
}

secure() {
    chmod 700 "$ENV_DIR"
    chmod 600 "$ENV_DIR"/*.env 2>/dev/null || true
    log "Permissions secured"
}

case "${1:-}" in
    init)    init ;;
    list)    list ;;
    create)  create "$2" ;;
    link)    link "$2" "$3" ;;
    copy)    copy "$2" "$3" ;;
    secure)  secure ;;
    *)
        echo "Environment File Manager"
        echo ""
        echo "Usage: $0 <command> [args]"
        echo ""
        echo "Commands:"
        echo "  init              Create env directory"
        echo "  list              List all env files"
        echo "  create <name>     Create new env file"
        echo "  link <name> <dir> Symlink env to project"
        echo "  copy <name> <dir> Copy env to project"
        echo "  secure            Fix permissions"
        ;;
esac
