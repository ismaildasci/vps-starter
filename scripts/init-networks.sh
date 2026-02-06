#!/usr/bin/env bash
# Create required Docker networks for VPS Starter
#
# Usage: ./init-networks.sh
#
# This script creates the external Docker networks required by various
# services in the VPS Starter stack. Run this before starting any services.

set -e

if ! docker info >/dev/null 2>&1; then
    echo "Error: Docker daemon is not running"
    exit 1
fi

networks=("web" "monitoring")

echo "Initializing Docker networks..."

for network in "${networks[@]}"; do
    if ! docker network inspect "$network" &>/dev/null; then
        echo "Creating network: $network"
        docker network create "$network"
    else
        echo "Network already exists: $network"
    fi
done

echo "All networks ready!"
