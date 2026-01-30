#!/bin/bash
#
# Hourly System Report Script
# Sends system metrics to Telegram
#
# Usage:
#   Export TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID before running
#   Or add to crontab: 0 * * * * /path/to/hourly-report.sh
#

# Telegram Bot credentials (set via environment variables)
BOT_TOKEN="${TELEGRAM_BOT_TOKEN}"
CHAT_ID="${TELEGRAM_CHAT_ID}"

# Check if credentials are set
if [ -z "$BOT_TOKEN" ] || [ -z "$CHAT_ID" ]; then
    echo "Error: TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set"
    exit 1
fi

# Gather system information
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1)
MEM_TOTAL=$(free -g | awk '/^Mem:/{print $2}')
MEM_USED=$(free -g | awk '/^Mem:/{print $3}')
MEM_PERCENT=$(free | awk '/^Mem:/{printf("%.1f", $3/$2*100)}')
DISK_TOTAL=$(df -h / | awk 'NR==2{print $2}')
DISK_USED=$(df -h / | awk 'NR==2{print $3}')
DISK_PERCENT=$(df -h / | awk 'NR==2{print $5}')
CONTAINER_COUNT=$(docker ps -q 2>/dev/null | wc -l)
UPTIME=$(uptime -p | sed 's/up //')

# Build message
MESSAGE="📊 <b>Hourly System Report</b>
━━━━━━━━━━━━━━━━━━━━

🖥️ <b>CPU:</b> ${CPU_USAGE}%

💾 <b>RAM:</b> ${MEM_USED}GB / ${MEM_TOTAL}GB (${MEM_PERCENT}%)

💿 <b>Disk:</b> ${DISK_USED} / ${DISK_TOTAL} (${DISK_PERCENT})

🐳 <b>Containers:</b> ${CONTAINER_COUNT} running

⏱️ <b>Uptime:</b> ${UPTIME}

🕐 $(date '+%Y-%m-%d %H:%M')"

# Send to Telegram
curl -s -X POST "https://api.telegram.org/bot${BOT_TOKEN}/sendMessage" \
  -d "chat_id=${CHAT_ID}" \
  -d "parse_mode=HTML" \
  -d "text=${MESSAGE}" > /dev/null

echo "Report sent: $(date)"
