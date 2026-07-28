#!/bin/bash
# Linkr control interface quick-call script
# Usage: ./send_control.sh '{"events":[["text","hello"],["delay",300]]}'

set -e

Linkr_IP="${Linkr_IP:-}"
Linkr_TOKEN="${Linkr_TOKEN:-}"
API_URL="http://${Linkr_IP}:80/api/public/control"

if [ $# -eq 0 ]; then
    echo "Usage: $0 '<json_payload>'"
    echo "Example:"
    echo "  $0 '{\"events\":[[\"text\",\"hello\"],[\"delay\",300]]}'"
    echo ""
    echo "Environment variables:"
    echo "  Linkr_IP - Linkr device IP (required, e.g. 192.168.x.x)"
    echo "  Linkr_TOKEN - Linkr access token (required)"
    exit 1
fi

if [ -z "${Linkr_IP}" ]; then
    echo "Error: Linkr_IP is required"
    exit 1
fi

if [ -z "${Linkr_TOKEN}" ]; then
    echo "Error: Linkr_TOKEN is required"
    exit 1
fi

echo "Sending request to: ${API_URL}"
curl -X POST "${API_URL}" \
    -H "Content-Type: application/json" \
    -H "Authorization: token ${Linkr_TOKEN}" \
    -d "$1"
