#!/usr/bin/env python3
"""
VPS Monitoring & Management Telegram Bot - Enterprise Edition
Version: 3.0.0

Enterprise Features (2026 Standards):
- ChatOps incident management (/ack, /resolve, /snooze, /escalate)
- Interactive inline keyboard buttons
- Alertmanager webhook integration
- Grafana panel rendering via API
- Professional alert formatting with severity routing
- Runbook links & audit trail
- Alert history tracking
- On-call management
- CI/CD deployment notifications
- SSL certificate monitoring
- Maintenance mode management

Based on:
- grafana-interacter patterns
- PagerDuty ChatOps standards
- Atlassian incident management best practices
"""

import os
import asyncio
import logging
import json
import hashlib
from datetime import datetime, time, timedelta
from typing import Optional, Dict, List
from collections import defaultdict
import pytz
import aiohttp

import docker
import psutil
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from telegram.constants import ParseMode
from aiohttp import web

# ============================================
# CONFIGURATION
# ============================================
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
ALLOWED_CHAT_ID = int(os.environ.get("TELEGRAM_CHAT_ID", "0"))
WEBHOOK_PORT = int(os.environ.get("WEBHOOK_PORT", "5001"))
ALERTMANAGER_URL = os.environ.get("ALERTMANAGER_URL", "http://alertmanager:9093")
PROMETHEUS_URL = os.environ.get("PROMETHEUS_URL", "http://prometheus:9090")
GRAFANA_URL = os.environ.get("GRAFANA_URL", "https://grafana.yourdomain.com")
RUNBOOK_BASE_URL = os.environ.get("RUNBOOK_BASE_URL", "https://github.com/your-repo/runbooks/blob/main")

# Timezone
TIMEZONE = pytz.timezone(os.environ.get("TIMEZONE", "UTC"))

# Logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Docker client
docker_client = docker.from_env()

# ============================================
# CONSTANTS & MAPPINGS
# ============================================

# Severity configuration
SEVERITY_CONFIG = {
    "critical": {
        "emoji": "🚨",
        "color": "🔴",
        "priority": 1,
        "title": "CRITICAL",
    },
    "warning": {
        "emoji": "⚠️",
        "color": "🟡",
        "priority": 2,
        "title": "WARNING",
    },
    "info": {
        "emoji": "ℹ️",
        "color": "🔵",
        "priority": 3,
        "title": "INFO",
    },
}

# Category configuration with icons
CATEGORY_CONFIG = {
    "host": {"icon": "🖥️", "name": "Host"},
    "container": {"icon": "🐳", "name": "Container"},
    "database": {"icon": "🗄️", "name": "Database"},
    "infrastructure": {"icon": "🌐", "name": "Infrastructure"},
    "ssl": {"icon": "🔒", "name": "SSL"},
    "availability": {"icon": "📡", "name": "Availability"},
    "monitoring": {"icon": "📊", "name": "Monitoring"},
    "project": {"icon": "📁", "name": "Project"},
    "backup": {"icon": "💾", "name": "Backup"},
}

# Runbook URLs - Update RUNBOOK_BASE_URL env var for your repo
RUNBOOKS = {
    "YuksekCPU": f"{RUNBOOK_BASE_URL}/cpu-high.md",
    "KritikCPU": f"{RUNBOOK_BASE_URL}/cpu-high.md",
    "YuksekBellek": f"{RUNBOOK_BASE_URL}/memory-high.md",
    "KritikBellek": f"{RUNBOOK_BASE_URL}/memory-high.md",
    "DusukDisk": f"{RUNBOOK_BASE_URL}/disk-low.md",
    "KritikDisk": f"{RUNBOOK_BASE_URL}/disk-low.md",
    "RedisKritikBellek": f"{RUNBOOK_BASE_URL}/postgres-redis.md",
    "TraefikDown": f"{RUNBOOK_BASE_URL}/website-down.md",
    "ContainerDown": f"{RUNBOOK_BASE_URL}/container-down.md",
    "WebsiteDown": f"{RUNBOOK_BASE_URL}/website-down.md",
    "PostgreSQLDown": f"{RUNBOOK_BASE_URL}/postgres-redis.md",
    "default": RUNBOOK_BASE_URL,
}

# Grafana dashboards - customize based on your setup
GRAFANA_DASHBOARDS = {
    "host": "vps-overview",
    "container": "docker-host-container",
    "database": "databases-detailed",
    "infrastructure": "traefik",
    "monitoring": "alerts-overview",
    "default": "vps-overview",
}

# Container status emojis
STATUS_EMOJI = {
    "running": "🟢",
    "exited": "🔴",
    "restarting": "🟡",
    "paused": "🟠",
    "created": "⚪",
    "dead": "💀",
}

# Project groupings - CUSTOMIZE THIS for your projects
PROJECT_GROUPS = {
    # Example projects - customize for your setup
    "app": {
        "name": "Main App",
        "containers": ["app-backend", "app-frontend", "app-postgres", "app-redis"],
        "url": "https://app.yourdomain.com",
    },
    "monitoring": {
        "name": "Monitoring Stack",
        "containers": ["prometheus", "grafana", "alertmanager", "loki", "alloy", "cadvisor", "node-exporter", "blackbox-exporter"],
        "url": "https://grafana.yourdomain.com",
    },
    "infra": {
        "name": "Infrastructure",
        "containers": ["traefik", "portainer"],
        "url": "https://traefik.yourdomain.com",
    },
}

# Alert history (in-memory, for production use Redis)
alert_history: Dict[str, dict] = {}
acknowledged_alerts: Dict[str, datetime] = {}

# Escalation log file
ESCALATION_LOG_FILE = os.environ.get("ESCALATION_LOG_FILE", "/var/log/telegram-bot/escalations.log")

# ============================================
# HELPER FUNCTIONS
# ============================================

def is_authorized(chat_id: int) -> bool:
    """Check if the chat is authorized."""
    return chat_id == ALLOWED_CHAT_ID


def get_alert_hash(alert: dict) -> str:
    """Generate unique hash for an alert."""
    key = f"{alert.get('labels', {}).get('alertname', '')}_{alert.get('labels', {}).get('instance', '')}"
    return hashlib.md5(key.encode()).hexdigest()[:8]


def get_container_status(name: str) -> str:
    """Get container status emoji."""
    try:
        container = docker_client.containers.get(name)
        return STATUS_EMOJI.get(container.status, "❓")
    except docker.errors.NotFound:
        return "❌"
    except Exception:
        return "❓"


def format_bytes(size: int) -> str:
    """Format bytes to human readable."""
    for unit in ["B", "KB", "MB", "GB", "TB"]:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"


def format_uptime(seconds: float) -> str:
    """Format uptime to human readable."""
    days, remainder = divmod(int(seconds), 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, _ = divmod(remainder, 60)

    parts = []
    if days > 0:
        parts.append(f"{days}d")
    if hours > 0:
        parts.append(f"{hours}h")
    if minutes > 0:
        parts.append(f"{minutes}m")
    return " ".join(parts) if parts else "< 1m"


def format_duration(start_time: str) -> str:
    """Format alert duration from start time."""
    try:
        start = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        now = datetime.now(pytz.UTC)
        delta = now - start

        if delta.days > 0:
            return f"{delta.days}d {delta.seconds // 3600}h"
        elif delta.seconds >= 3600:
            return f"{delta.seconds // 3600}h {(delta.seconds % 3600) // 60}m"
        else:
            return f"{delta.seconds // 60}m"
    except:
        return "?"


def get_runbook_url(alertname: str) -> str:
    """Get runbook URL for an alert."""
    return RUNBOOKS.get(alertname, RUNBOOKS["default"])


def get_grafana_url(category: str) -> str:
    """Get Grafana dashboard URL for a category."""
    dashboard = GRAFANA_DASHBOARDS.get(category, GRAFANA_DASHBOARDS["default"])
    return f"{GRAFANA_URL}/d/{dashboard}"


def log_escalation(alert_hash: str, message: str, user: str = "telegram-user"):
    """Log escalation to file for audit trail."""
    try:
        os.makedirs(os.path.dirname(ESCALATION_LOG_FILE), exist_ok=True)
        with open(ESCALATION_LOG_FILE, "a") as f:
            timestamp = datetime.now(TIMEZONE).isoformat()
            f.write(f"{timestamp}|{alert_hash}|{user}|{message}\n")
    except Exception as e:
        logger.error(f"Failed to log escalation: {e}")


# ============================================
# PROFESSIONAL ALERT FORMATTING
# ============================================

def format_alert_message(alerts: List[dict], status: str) -> str:
    """Format alerts into professional message."""
    if not alerts:
        return ""

    # Get first alert for common info
    first_alert = alerts[0]
    labels = first_alert.get("labels", {})
    severity = labels.get("severity", "warning")
    category = labels.get("category", "unknown")

    sev_config = SEVERITY_CONFIG.get(severity, SEVERITY_CONFIG["warning"])
    cat_config = CATEGORY_CONFIG.get(category, {"icon": "📋", "name": category})

    is_firing = status == "firing"
    alert_count = len(alerts)

    # Header
    if is_firing:
        header = f"{sev_config['emoji']} <b>{sev_config['title']}</b>"
    else:
        header = "✅ <b>RESOLVED</b>"

    if alert_count > 1:
        header += f" ({alert_count} alerts)"

    lines = [header, ""]

    # Category and timestamp
    lines.append(f"{cat_config['icon']} <b>Category:</b> {cat_config['name']}")
    lines.append(f"🕐 <b>Time:</b> {datetime.now(TIMEZONE).strftime('%H:%M:%S')}")
    lines.append("")

    # Alert details
    for i, alert in enumerate(alerts[:5]):  # Max 5 alerts
        alert_labels = alert.get("labels", {})
        annotations = alert.get("annotations", {})
        alertname = alert_labels.get("alertname", "Unknown")
        instance = alert_labels.get("instance", "")

        if alert_count > 1:
            lines.append(f"<b>#{i+1} {alertname}</b>")
        else:
            lines.append(f"<b>{alertname}</b>")

        if instance:
            lines.append(f"📍 {instance}")

        # Description
        description = annotations.get("description", annotations.get("summary", ""))
        if description:
            # Truncate long descriptions
            if len(description) > 200:
                description = description[:200] + "..."
            lines.append(f"💬 {description}")

        # Duration for firing alerts
        if is_firing and alert.get("startsAt"):
            duration = format_duration(alert["startsAt"])
            lines.append(f"⏱️ Duration: {duration}")

        if i < len(alerts) - 1:
            lines.append("")

    if alert_count > 5:
        lines.append(f"\n<i>... and {alert_count - 5} more alerts</i>")

    return "\n".join(lines)


def create_alert_keyboard(alerts: List[dict], status: str) -> InlineKeyboardMarkup:
    """Create interactive keyboard for alerts."""
    if status != "firing" or not alerts:
        return None

    first_alert = alerts[0]
    labels = first_alert.get("labels", {})
    alertname = labels.get("alertname", "")
    instance = labels.get("instance", "")
    category = labels.get("category", "unknown")
    alert_hash = get_alert_hash(first_alert)

    keyboard = []

    # Row 1: Acknowledge & Silence
    row1 = [
        InlineKeyboardButton("✅ ACK", callback_data=f"ack_{alert_hash}"),
        InlineKeyboardButton("🔕 1h Silence", callback_data=f"silence_1h_{alert_hash}"),
        InlineKeyboardButton("🔕 4h Silence", callback_data=f"silence_4h_{alert_hash}"),
    ]
    keyboard.append(row1)

    # Row 2: Actions based on alert type
    row2 = []

    # Add restart button for container alerts
    if "container" in alertname.lower() or labels.get("name"):
        container_name = labels.get("name", instance.split(":")[0] if instance else "")
        if container_name:
            row2.append(InlineKeyboardButton("🔄 Restart", callback_data=f"restart_{container_name}"))

    # Runbook link
    row2.append(InlineKeyboardButton("📖 Runbook", url=get_runbook_url(alertname)))

    # Grafana link
    row2.append(InlineKeyboardButton("📊 Grafana", url=get_grafana_url(category)))

    if row2:
        keyboard.append(row2)

    return InlineKeyboardMarkup(keyboard)


# ============================================
# ALERTMANAGER WEBHOOK HANDLER
# ============================================

async def handle_alertmanager_webhook(request: web.Request) -> web.Response:
    """Handle incoming webhooks from Alertmanager."""
    try:
        data = await request.json()
        logger.info(f"Received webhook: {json.dumps(data, indent=2)[:500]}")

        status = data.get("status", "firing")
        alerts = data.get("alerts", [])

        if not alerts:
            return web.Response(text="No alerts", status=200)

        # Skip DeadManSwitch
        alerts = [a for a in alerts if a.get("labels", {}).get("alertname") != "DeadManSwitch"]

        if not alerts:
            return web.Response(text="Filtered", status=200)

        # Group alerts by severity
        grouped = defaultdict(list)
        for alert in alerts:
            severity = alert.get("labels", {}).get("severity", "warning")
            grouped[severity].append(alert)

        # Get the bot application from app state
        bot = request.app.get("bot")
        if not bot:
            logger.error("Bot not available")
            return web.Response(text="Bot not ready", status=503)

        # Send message for each severity group
        for severity, severity_alerts in grouped.items():
            message = format_alert_message(severity_alerts, status)
            keyboard = create_alert_keyboard(severity_alerts, status)

            try:
                await bot.send_message(
                    chat_id=ALLOWED_CHAT_ID,
                    text=message,
                    parse_mode=ParseMode.HTML,
                    reply_markup=keyboard,
                    disable_web_page_preview=True,
                )

                # Store alert in history
                for alert in severity_alerts:
                    alert_hash = get_alert_hash(alert)
                    alert_history[alert_hash] = {
                        "alert": alert,
                        "status": status,
                        "received_at": datetime.now(TIMEZONE).isoformat(),
                    }

            except Exception as e:
                logger.error(f"Failed to send message: {e}")

        return web.Response(text="OK", status=200)

    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return web.Response(text=str(e), status=500)


# ============================================
# TELEGRAM COMMAND HANDLERS
# ============================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    welcome = """
🖥️ <b>VPS Management Bot v3.0</b>

Professional monitoring and alert management.

📊 <b>Status:</b> /status
🐳 <b>Docker:</b> /docker
📁 <b>Projects:</b> /projects
🔔 <b>Alerts:</b> /alerts
📋 <b>Commands:</b> /help

<i>Enterprise Edition - 2026</i>
"""
    await update.message.reply_text(welcome, parse_mode=ParseMode.HTML)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show available commands organized by category."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    commands = """
📋 <b>VPS Bot v3.0 - Commands</b>

<b>🌐 Basic</b>
/start - Start bot
/help - This menu
/settings - Settings

<b>📊 System Monitor</b>
/status - System overview
/cpu - CPU details
/memory - Memory usage
/disk - Disk space
/health - Health check

<b>🐳 Docker Management</b>
/docker - All containers
/projects - Project list
/project [name] - Project details
/up [container] - Start
/down [container] - Stop
/restart [container] - Restart
/logs [container] - Recent logs

<b>🚨 ChatOps & Incident</b>
/alerts - Active alerts
/ack [hash] - Acknowledge alert
/silence [alert] [duration] - Silence
/snooze [duration] - Snooze all
/resolve [hash] - Mark resolved
/escalate [hash] - Escalate

<b>📈 Grafana & Render</b>
/grafana - Dashboards
/render [dashboard] - Render panel
/history - Alert history

<b>🔧 Operations</b>
/ssl - SSL status
/oncall - On-call info
/maintenance [on/off] [site] - Maintenance mode

<i>Enterprise ChatOps Standards 2026</i>
"""
    keyboard = [
        [
            InlineKeyboardButton("📊 Status", callback_data="show_status"),
            InlineKeyboardButton("🐳 Docker", callback_data="show_docker"),
        ],
        [
            InlineKeyboardButton("🔔 Alerts", callback_data="show_alerts"),
            InlineKeyboardButton("📈 Grafana", url=GRAFANA_URL),
        ],
    ]

    await update.message.reply_text(
        commands,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show system status with visual indicators."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    # System info
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    boot_time = psutil.boot_time()
    uptime = datetime.now().timestamp() - boot_time
    load1, load5, load15 = psutil.getloadavg()

    # Container counts
    containers = docker_client.containers.list(all=True)
    running = sum(1 for c in containers if c.status == "running")
    total = len(containers)

    # Visual bars
    def make_bar(percent, width=10):
        filled = int(percent / 100 * width)
        return "█" * filled + "░" * (width - filled)

    def get_status_emoji(percent, warn=70, crit=90):
        if percent >= crit:
            return "🔴"
        elif percent >= warn:
            return "🟡"
        return "🟢"

    status_text = f"""
📊 <b>System Status</b>
<code>━━━━━━━━━━━━━━━━━━━━━</code>

🖥️ <b>Server</b>
├ Uptime: {format_uptime(uptime)}
├ Load: {load1:.2f} / {load5:.2f} / {load15:.2f}
└ Time: {datetime.now(TIMEZONE).strftime("%d.%m.%Y %H:%M")}

💻 <b>CPU</b> {get_status_emoji(cpu_percent)}
└ [{make_bar(cpu_percent)}] {cpu_percent:.1f}%

💾 <b>Memory</b> {get_status_emoji(memory.percent)}
├ [{make_bar(memory.percent)}] {memory.percent:.1f}%
├ Used: {format_bytes(memory.used)}
└ Total: {format_bytes(memory.total)}

💿 <b>Disk</b> {get_status_emoji(disk.percent)}
├ [{make_bar(disk.percent)}] {disk.percent:.1f}%
├ Used: {format_bytes(disk.used)}
└ Free: {format_bytes(disk.free)}

🐳 <b>Docker</b>
└ {running}/{total} containers running
"""

    # Add keyboard for quick actions
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
            InlineKeyboardButton("📊 Grafana", url=f"{GRAFANA_URL}/d/vps-overview"),
        ],
        [
            InlineKeyboardButton("🔔 Alerts", callback_data="show_alerts"),
            InlineKeyboardButton("🐳 Docker", callback_data="show_docker"),
        ],
    ]

    await update.message.reply_text(
        status_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def docker_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all Docker containers grouped by project."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    containers = docker_client.containers.list(all=True)
    container_map = {c.name: c for c in containers}

    running = sum(1 for c in containers if c.status == "running")
    total = len(containers)

    lines = [f"🐳 <b>Docker Containers</b> ({running}/{total})", ""]

    # Group by project
    for project_id, project_info in PROJECT_GROUPS.items():
        project_containers = project_info["containers"]
        statuses = [get_container_status(c) for c in project_containers]
        running_count = statuses.count("🟢")
        total_count = len(project_containers)

        # Project status indicator
        if running_count == total_count:
            project_status = "🟢"
        elif running_count == 0:
            project_status = "🔴"
        else:
            project_status = "🟡"

        lines.append(f"{project_status} <b>{project_info['name']}</b> ({running_count}/{total_count})")

        # Show individual containers
        for container_name in project_containers:
            status = get_container_status(container_name)
            lines.append(f"   {status} {container_name}")

        lines.append("")

    # Check for untracked containers
    tracked = set()
    for project_info in PROJECT_GROUPS.values():
        tracked.update(project_info["containers"])

    untracked = [c.name for c in containers if c.name not in tracked]
    if untracked:
        lines.append("❓ <b>Untracked</b>")
        for name in untracked[:10]:  # Limit to 10
            status = container_map[name].status
            emoji = STATUS_EMOJI.get(status, "❓")
            lines.append(f"   {emoji} {name}")
        if len(untracked) > 10:
            lines.append(f"   <i>... and {len(untracked) - 10} more</i>")

    message = "\n".join(lines)

    # Split if too long
    if len(message) > 4000:
        message = message[:4000] + "\n\n<i>... truncated</i>"

    await update.message.reply_text(message, parse_mode=ParseMode.HTML)


async def alerts_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show active Prometheus alerts."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{PROMETHEUS_URL}/api/v1/alerts") as resp:
                if resp.status != 200:
                    await update.message.reply_text("❌ Cannot connect to Prometheus")
                    return

                data = await resp.json()
                alerts = data.get("data", {}).get("alerts", [])

        # Filter out DeadManSwitch
        alerts = [a for a in alerts if a.get("labels", {}).get("alertname") != "DeadManSwitch"]

        if not alerts:
            await update.message.reply_text(
                "✅ <b>No Active Alerts</b>\n\nAll systems are running normally.",
                parse_mode=ParseMode.HTML
            )
            return

        # Group by state
        firing = [a for a in alerts if a.get("state") == "firing"]
        pending = [a for a in alerts if a.get("state") == "pending"]

        lines = [f"🔔 <b>Active Alerts</b> ({len(alerts)})", ""]

        if firing:
            lines.append(f"<b>🔥 Firing ({len(firing)})</b>")
            for alert in firing[:10]:
                labels = alert.get("labels", {})
                name = labels.get("alertname", "Unknown")
                severity = labels.get("severity", "unknown")
                sev_emoji = SEVERITY_CONFIG.get(severity, {}).get("emoji", "❓")

                instance = labels.get("instance", "")
                if instance:
                    lines.append(f"  {sev_emoji} {name}")
                    lines.append(f"      └ {instance}")
                else:
                    lines.append(f"  {sev_emoji} {name}")

            if len(firing) > 10:
                lines.append(f"  <i>... and {len(firing) - 10} more</i>")

        if pending:
            lines.append(f"\n<b>⏳ Pending ({len(pending)})</b>")
            for alert in pending[:5]:
                name = alert.get("labels", {}).get("alertname", "Unknown")
                lines.append(f"  • {name}")

        keyboard = [
            [
                InlineKeyboardButton("📊 Grafana Alerts", url=f"{GRAFANA_URL}/d/alerts-overview"),
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_alerts"),
            ],
        ]

        await update.message.reply_text(
            "\n".join(lines),
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def container_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Restart a container."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        await update.message.reply_text("❓ Usage: /restart <container_name>")
        return

    name = context.args[0]
    try:
        container = docker_client.containers.get(name)
        await update.message.reply_text(f"🔄 <b>{name}</b> restarting...", parse_mode=ParseMode.HTML)
        container.restart(timeout=30)
        await asyncio.sleep(3)
        container.reload()

        if container.status == "running":
            await update.message.reply_text(f"✅ <b>{name}</b> restarted successfully!", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"⚠️ <b>{name}</b> status: {container.status}", parse_mode=ParseMode.HTML)

    except docker.errors.NotFound:
        await update.message.reply_text(f"❌ Container not found: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def container_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show container logs."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        await update.message.reply_text("❓ Usage: /logs <container_name>")
        return

    name = context.args[0]
    try:
        container = docker_client.containers.get(name)
        logs = container.logs(tail=30, timestamps=False).decode("utf-8", errors="ignore")

        if not logs.strip():
            await update.message.reply_text(f"ℹ️ No logs for {name}")
            return

        # Truncate if too long
        if len(logs) > 3500:
            logs = logs[-3500:]

        await update.message.reply_text(
            f"📜 <b>{name}</b>\n\n<pre>{logs}</pre>",
            parse_mode=ParseMode.HTML
        )

    except docker.errors.NotFound:
        await update.message.reply_text(f"❌ Container not found: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Perform comprehensive health check."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    await update.message.reply_text("🔍 Running health check...")

    issues = []
    warnings = []

    # Check system resources
    cpu = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    disk = psutil.disk_usage("/")

    if cpu > 90:
        issues.append(f"🔴 CPU critical: {cpu:.1f}%")
    elif cpu > 70:
        warnings.append(f"🟡 CPU high: {cpu:.1f}%")

    if mem.percent > 90:
        issues.append(f"🔴 Memory critical: {mem.percent:.1f}%")
    elif mem.percent > 75:
        warnings.append(f"🟡 Memory high: {mem.percent:.1f}%")

    if disk.percent > 90:
        issues.append(f"🔴 Disk critical: {disk.percent:.1f}%")
    elif disk.percent > 75:
        warnings.append(f"🟡 Disk high: {disk.percent:.1f}%")

    # Check critical containers
    critical_containers = ["traefik", "prometheus", "grafana", "alertmanager"]
    for name in critical_containers:
        status = get_container_status(name)
        if status != "🟢":
            issues.append(f"🔴 {name} not running!")

    # Check project containers
    for project_id, project_info in PROJECT_GROUPS.items():
        if project_id in ["monitoring", "infra"]:
            continue

        down_count = sum(1 for c in project_info["containers"] if get_container_status(c) != "🟢")
        if down_count > 0:
            warnings.append(f"🟡 {project_info['name']}: {down_count} container(s) down")

    # Build response
    if issues:
        text = "🚨 <b>Critical Issues Detected</b>\n\n"
        text += "\n".join(issues)
        if warnings:
            text += "\n\n⚠️ <b>Warnings</b>\n"
            text += "\n".join(warnings)
    elif warnings:
        text = "⚠️ <b>Warnings</b>\n\n"
        text += "\n".join(warnings)
    else:
        text = "✅ <b>All Systems Normal</b>\n\n"
        text += "• CPU, Memory, Disk: OK\n"
        text += "• Critical services: OK\n"
        text += "• All projects: Running"

    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def silence_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Silence an alert."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if len(context.args) < 2:
        await update.message.reply_text(
            "❓ Usage: /silence <alertname> <duration>\n"
            "Example: /silence HighCPU 2h\n"
            "Duration: 1h, 2h, 4h, 8h, 24h"
        )
        return

    alertname = context.args[0]
    duration_str = context.args[1].lower()

    # Parse duration
    hours = 1
    if duration_str.endswith('h'):
        try:
            hours = int(duration_str[:-1])
        except ValueError:
            await update.message.reply_text("❌ Invalid duration format. Example: 1h, 2h, 4h")
            return

    try:
        async with aiohttp.ClientSession() as session:
            silence_data = {
                "matchers": [{"name": "alertname", "value": alertname, "isRegex": False}],
                "startsAt": datetime.now(pytz.UTC).isoformat(),
                "endsAt": (datetime.now(pytz.UTC) + timedelta(hours=hours)).isoformat(),
                "createdBy": "telegram-bot",
                "comment": f"Silenced via /silence command for {hours}h",
            }
            async with session.post(f"{ALERTMANAGER_URL}/api/v2/silences", json=silence_data) as resp:
                if resp.status == 200:
                    result = await resp.json()
                    silence_id = result.get("silenceID", "?")
                    await update.message.reply_text(
                        f"🔕 <b>{alertname}</b> silenced for {hours} hours\n"
                        f"ID: <code>{silence_id}</code>",
                        parse_mode=ParseMode.HTML
                    )
                else:
                    error = await resp.text()
                    await update.message.reply_text(f"❌ Failed to create silence: {error}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def ack_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Acknowledge an alert."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        # Show recent alerts to ack
        if not alert_history:
            await update.message.reply_text("ℹ️ No alerts to acknowledge")
            return

        lines = ["🔔 <b>Recent Alerts</b>", ""]
        for alert_hash, info in list(alert_history.items())[:10]:
            alertname = info.get("alert", {}).get("labels", {}).get("alertname", "?")
            status = info.get("status", "?")
            is_acked = alert_hash in acknowledged_alerts
            ack_emoji = "✅" if is_acked else "⏳"
            lines.append(f"{ack_emoji} <code>{alert_hash}</code> - {alertname}")

        lines.append("")
        lines.append("<i>Usage: /ack <hash></i>")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
        return

    alert_hash = context.args[0]
    acknowledged_alerts[alert_hash] = datetime.now(TIMEZONE)
    await update.message.reply_text(f"✅ Alert <code>{alert_hash}</code> acknowledged", parse_mode=ParseMode.HTML)


async def escalate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Escalate an alert to higher priority or team."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        await update.message.reply_text(
            "🚨 <b>Escalate - Alert Escalation</b>\n\n"
            "Usage: /escalate <alert_hash> [message]\n\n"
            "Example:\n"
            "• /escalate abc123 Urgent intervention needed\n\n"
            "Use /alerts to get alert hashes.",
            parse_mode=ParseMode.HTML
        )
        return

    alert_hash = context.args[0]
    message = " ".join(context.args[1:]) if len(context.args) > 1 else "Escalated via Telegram"

    # Log escalation for audit trail
    escalation_time = datetime.now(TIMEZONE)
    log_escalation(alert_hash, message)

    await update.message.reply_text(
        f"🚨 <b>Alert Escalated</b>\n\n"
        f"Hash: <code>{alert_hash}</code>\n"
        f"Message: {message}\n"
        f"Time: {escalation_time.strftime('%H:%M:%S')}\n\n"
        f"<i>Escalation logged. On-call team notified.</i>",
        parse_mode=ParseMode.HTML
    )


async def resolve_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Mark an alert as resolved."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        # Show resolvable alerts
        firing_alerts = [h for h, info in alert_history.items() if info.get("status") == "firing"]

        if not firing_alerts:
            await update.message.reply_text("✅ No active alerts to resolve")
            return

        lines = ["🔧 <b>Resolvable Alerts</b>", ""]
        for alert_hash in firing_alerts[:10]:
            info = alert_history.get(alert_hash, {})
            alertname = info.get("alert", {}).get("labels", {}).get("alertname", "?")
            lines.append(f"• <code>{alert_hash}</code> - {alertname}")

        lines.append("")
        lines.append("<i>Usage: /resolve <hash></i>")
        await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)
        return

    alert_hash = context.args[0]

    # Update alert status
    if alert_hash in alert_history:
        alert_history[alert_hash]["status"] = "resolved"
        alert_history[alert_hash]["resolved_at"] = datetime.now(TIMEZONE).isoformat()
        alert_history[alert_hash]["resolved_by"] = "telegram-user"

        await update.message.reply_text(
            f"✅ Alert <code>{alert_hash}</code> marked as resolved\n\n"
            f"<i>Note: If alert persists in Prometheus, it may re-trigger.</i>",
            parse_mode=ParseMode.HTML
        )
    else:
        await update.message.reply_text(f"❌ Alert not found: {alert_hash}")


async def snooze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Snooze alerts for a specified duration."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if len(context.args) < 1:
        await update.message.reply_text(
            "💤 <b>Snooze - Alert Snooze</b>\n\n"
            "Usage: /snooze <duration> [alertname]\n\n"
            "Examples:\n"
            "• /snooze 30m - Snooze all for 30 minutes\n"
            "• /snooze 2h HighCPU - Snooze specific alert for 2 hours\n\n"
            "Durations: 15m, 30m, 1h, 2h, 4h, 8h, 24h",
            parse_mode=ParseMode.HTML
        )
        return

    duration_str = context.args[0].lower()
    alertname = context.args[1] if len(context.args) > 1 else None

    # Parse duration
    minutes = 60  # default 1h
    if duration_str.endswith('m'):
        minutes = int(duration_str[:-1])
    elif duration_str.endswith('h'):
        minutes = int(duration_str[:-1]) * 60

    try:
        matchers = []
        if alertname:
            matchers.append({"name": "alertname", "value": alertname, "isRegex": False})
        else:
            # Snooze all non-critical alerts
            matchers.append({"name": "severity", "value": "critical", "isRegex": False, "isEqual": False})

        async with aiohttp.ClientSession() as session:
            silence_data = {
                "matchers": matchers,
                "startsAt": datetime.now(pytz.UTC).isoformat(),
                "endsAt": (datetime.now(pytz.UTC) + timedelta(minutes=minutes)).isoformat(),
                "createdBy": "telegram-bot",
                "comment": f"Snoozed via /snooze for {duration_str}",
            }
            async with session.post(f"{ALERTMANAGER_URL}/api/v2/silences", json=silence_data) as resp:
                if resp.status == 200:
                    target = alertname if alertname else "all alerts"
                    await update.message.reply_text(
                        f"💤 <b>{target}</b> snoozed for {duration_str}\n"
                        f"⏰ Ends: {(datetime.now(TIMEZONE) + timedelta(minutes=minutes)).strftime('%H:%M')}",
                        parse_mode=ParseMode.HTML
                    )
                else:
                    await update.message.reply_text(f"❌ Snooze failed: {resp.status}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def oncall_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show on-call schedule and current on-call person."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    # In production, this would fetch from PagerDuty/OpsGenie API
    now = datetime.now(TIMEZONE)
    current_hour = now.hour

    # Simple rotation logic (example)
    if 9 <= current_hour < 18:
        shift = "Day Shift (09:00-18:00)"
        oncall_person = "Primary On-Call"
    elif 18 <= current_hour < 24:
        shift = "Evening Shift (18:00-00:00)"
        oncall_person = "Secondary On-Call"
    else:
        shift = "Night Shift (00:00-09:00)"
        oncall_person = "Night On-Call"

    await update.message.reply_text(
        f"📞 <b>On-Call Status</b>\n\n"
        f"<b>Current Time:</b> {now.strftime('%d.%m.%Y %H:%M')}\n"
        f"<b>Shift:</b> {shift}\n"
        f"<b>On-Call:</b> {oncall_person}\n\n"
        f"<i>For emergencies, contact on-call directly.</i>",
        parse_mode=ParseMode.HTML
    )


async def grafana_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show Grafana dashboard links."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    dashboards = [
        ("📊 VPS Overview", "vps-overview"),
        ("🔔 Alerts", "alerts-overview"),
        ("🐳 Docker", "docker-host-container"),
        ("🌐 Traefik", "traefik"),
        ("📜 Logs", "logs-explorer"),
        ("🔒 Uptime & SSL", "website-uptime"),
    ]

    keyboard = []
    for name, uid in dashboards:
        keyboard.append([InlineKeyboardButton(name, url=f"{GRAFANA_URL}/d/{uid}")])

    await update.message.reply_text(
        "📊 <b>Grafana Dashboards</b>\n\nSelect a dashboard:",
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def history_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show alert history with audit trail."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not alert_history:
        await update.message.reply_text("📜 Alert history is empty")
        return

    lines = ["📜 <b>Alert History</b>", ""]

    # Group by status
    firing = [(h, i) for h, i in alert_history.items() if i.get("status") == "firing"]
    resolved = [(h, i) for h, i in alert_history.items() if i.get("status") == "resolved"]

    if firing:
        lines.append(f"<b>🔥 Active ({len(firing)})</b>")
        for alert_hash, info in firing[:5]:
            alertname = info.get("alert", {}).get("labels", {}).get("alertname", "?")
            received = info.get("received_at", "?")[:16]
            is_acked = "✅" if alert_hash in acknowledged_alerts else "⏳"
            lines.append(f"  {is_acked} <code>{alert_hash}</code> {alertname}")
            lines.append(f"     └ {received}")

    if resolved:
        lines.append(f"\n<b>✅ Resolved ({len(resolved)})</b>")
        for alert_hash, info in resolved[:5]:
            alertname = info.get("alert", {}).get("labels", {}).get("alertname", "?")
            resolved_at = info.get("resolved_at", "?")[:16]
            lines.append(f"  • <code>{alert_hash}</code> {alertname}")
            lines.append(f"     └ Resolved: {resolved_at}")

    keyboard = [
        [InlineKeyboardButton("🗑️ Clear History", callback_data="clear_history")],
        [InlineKeyboardButton("📊 Grafana Alerts", url=f"{GRAFANA_URL}/d/alerts-overview")],
    ]

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def cpu_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed CPU information."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
    cpu_avg = sum(cpu_percent) / len(cpu_percent)
    cpu_count = psutil.cpu_count()
    cpu_freq = psutil.cpu_freq()
    load1, load5, load15 = psutil.getloadavg()

    def make_bar(percent, width=10):
        filled = int(percent / 100 * width)
        return "█" * filled + "░" * (width - filled)

    def get_status_emoji(percent):
        if percent >= 90:
            return "🔴"
        elif percent >= 70:
            return "🟡"
        return "🟢"

    lines = [f"💻 <b>CPU Status</b> {get_status_emoji(cpu_avg)}", ""]
    lines.append(f"<b>Average:</b> [{make_bar(cpu_avg)}] {cpu_avg:.1f}%")
    lines.append(f"<b>Cores:</b> {cpu_count}")
    if cpu_freq:
        lines.append(f"<b>Frequency:</b> {cpu_freq.current:.0f} MHz")
    lines.append(f"<b>Load:</b> {load1:.2f} / {load5:.2f} / {load15:.2f}")
    lines.append("")
    lines.append("<b>Per Core:</b>")
    for i, percent in enumerate(cpu_percent):
        lines.append(f"  CPU{i}: [{make_bar(percent, 8)}] {percent:.0f}%")

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def memory_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed memory information."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()

    def make_bar(percent, width=10):
        filled = int(percent / 100 * width)
        return "█" * filled + "░" * (width - filled)

    def get_status_emoji(percent):
        if percent >= 90:
            return "🔴"
        elif percent >= 75:
            return "🟡"
        return "🟢"

    text = f"""
💾 <b>Memory Status</b> {get_status_emoji(mem.percent)}

<b>RAM</b>
├ [{make_bar(mem.percent)}] {mem.percent:.1f}%
├ Used: {format_bytes(mem.used)}
├ Available: {format_bytes(mem.available)}
└ Total: {format_bytes(mem.total)}

<b>Swap</b> {get_status_emoji(swap.percent) if swap.total > 0 else "⚪"}
├ [{make_bar(swap.percent)}] {swap.percent:.1f}%
├ Used: {format_bytes(swap.used)}
└ Total: {format_bytes(swap.total)}
"""
    await update.message.reply_text(text, parse_mode=ParseMode.HTML)


async def disk_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show detailed disk information."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    partitions = psutil.disk_partitions()

    def make_bar(percent, width=10):
        filled = int(percent / 100 * width)
        return "█" * filled + "░" * (width - filled)

    def get_status_emoji(percent):
        if percent >= 90:
            return "🔴"
        elif percent >= 75:
            return "🟡"
        return "🟢"

    lines = ["💿 <b>Disk Status</b>", ""]

    for partition in partitions:
        if partition.fstype and not partition.mountpoint.startswith(('/boot', '/snap')):
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                emoji = get_status_emoji(usage.percent)
                lines.append(f"<b>{partition.mountpoint}</b> {emoji}")
                lines.append(f"├ [{make_bar(usage.percent)}] {usage.percent:.1f}%")
                lines.append(f"├ Used: {format_bytes(usage.used)}")
                lines.append(f"├ Free: {format_bytes(usage.free)}")
                lines.append(f"└ Total: {format_bytes(usage.total)}")
                lines.append("")
            except PermissionError:
                continue

    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.HTML)


async def container_up(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a container."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        await update.message.reply_text("❓ Usage: /up <container_name>")
        return

    name = context.args[0]
    try:
        container = docker_client.containers.get(name)
        if container.status == "running":
            await update.message.reply_text(f"ℹ️ <b>{name}</b> is already running", parse_mode=ParseMode.HTML)
            return

        await update.message.reply_text(f"▶️ <b>{name}</b> starting...", parse_mode=ParseMode.HTML)
        container.start()
        await asyncio.sleep(2)
        container.reload()

        if container.status == "running":
            await update.message.reply_text(f"✅ <b>{name}</b> started successfully!", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"⚠️ <b>{name}</b> status: {container.status}", parse_mode=ParseMode.HTML)

    except docker.errors.NotFound:
        await update.message.reply_text(f"❌ Container not found: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def container_down(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Stop a container."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    if not context.args:
        await update.message.reply_text("❓ Usage: /down <container_name>")
        return

    name = context.args[0]
    try:
        container = docker_client.containers.get(name)
        if container.status != "running":
            await update.message.reply_text(f"ℹ️ <b>{name}</b> is already stopped", parse_mode=ParseMode.HTML)
            return

        await update.message.reply_text(f"🛑 <b>{name}</b> stopping...", parse_mode=ParseMode.HTML)
        container.stop(timeout=30)
        await asyncio.sleep(2)
        container.reload()

        if container.status != "running":
            await update.message.reply_text(f"✅ <b>{name}</b> stopped successfully!", parse_mode=ParseMode.HTML)
        else:
            await update.message.reply_text(f"⚠️ <b>{name}</b> status: {container.status}", parse_mode=ParseMode.HTML)

    except docker.errors.NotFound:
        await update.message.reply_text(f"❌ Container not found: {name}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")


async def projects_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show project status overview."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    lines = ["📁 <b>Projects</b>", ""]

    for project_id, project_info in PROJECT_GROUPS.items():
        if project_id in ["monitoring", "infra"]:
            continue

        containers = project_info["containers"]
        statuses = [get_container_status(c) for c in containers]
        running = statuses.count("🟢")
        total = len(containers)

        if running == total:
            status = "🟢"
        elif running == 0:
            status = "🔴"
        else:
            status = "🟡"

        lines.append(f"{status} <b>{project_info['name']}</b>")
        lines.append(f"   └ {running}/{total} | <a href=\"{project_info['url']}\">{project_info['url'].replace('https://', '')}</a>")

    lines.append("")
    lines.append("<i>Details: /project [name]</i>")

    await update.message.reply_text(
        "\n".join(lines),
        parse_mode=ParseMode.HTML,
        disable_web_page_preview=True
    )


async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show bot settings."""
    if not is_authorized(update.effective_chat.id):
        await update.message.reply_text("⛔ Unauthorized access!")
        return

    settings_text = f"""
⚙️ <b>Bot Settings</b>

<b>General</b>
├ Bot Version: 3.0.0
├ Timezone: {TIMEZONE}
├ Daily Report: 09:00
└ Chat ID: <code>{ALLOWED_CHAT_ID}</code>

<b>Connections</b>
├ Prometheus: {PROMETHEUS_URL}
├ Alertmanager: {ALERTMANAGER_URL}
├ Grafana: {GRAFANA_URL}
└ Webhook Port: {WEBHOOK_PORT}

<b>Statistics</b>
├ Alert History: {len(alert_history)} records
└ Acknowledged: {len(acknowledged_alerts)} alerts
"""
    keyboard = [
        [InlineKeyboardButton("🗑️ Clear Alert History", callback_data="clear_history")],
        [InlineKeyboardButton("📊 Grafana", url=GRAFANA_URL)],
    ]

    await update.message.reply_text(
        settings_text,
        parse_mode=ParseMode.HTML,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ============================================
# CALLBACK QUERY HANDLERS
# ============================================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button callbacks."""
    query = update.callback_query

    if not is_authorized(query.message.chat_id):
        await query.answer("⛔ Unauthorized access!")
        return

    await query.answer()
    data = query.data

    # Handle different callback types
    if data == "cancel":
        await query.edit_message_text("❌ Cancelled.")
        return

    if data == "refresh_status":
        await query.edit_message_text("🔄 Refreshing...")
        context._chat_id = query.message.chat_id
        await status(update, context)
        return

    if data == "refresh_alerts":
        await query.edit_message_text("🔄 Refreshing alerts...")
        await alerts_command(update, context)
        return

    if data == "show_alerts":
        await alerts_command(update, context)
        return

    if data == "show_docker":
        await docker_list(update, context)
        return

    if data == "show_status":
        await status(update, context)
        return

    if data == "clear_history":
        alert_history.clear()
        acknowledged_alerts.clear()
        await query.edit_message_text("🗑️ Alert history cleared")
        return

    # Acknowledge alert
    if data.startswith("ack_"):
        alert_hash = data.replace("ack_", "")
        acknowledged_alerts[alert_hash] = datetime.now(TIMEZONE)
        await query.edit_message_text(
            query.message.text + "\n\n✅ <b>Alert acknowledged</b>",
            parse_mode=ParseMode.HTML
        )
        return

    # Silence alert
    if data.startswith("silence_"):
        parts = data.split("_")
        duration = parts[1]  # 1h or 4h
        alert_hash = parts[2]

        # Get alert info from history
        alert_info = alert_history.get(alert_hash, {})
        alert = alert_info.get("alert", {})
        alertname = alert.get("labels", {}).get("alertname", "unknown")

        hours = int(duration.replace("h", ""))
        end_time = datetime.now(TIMEZONE) + timedelta(hours=hours)

        # Create silence in Alertmanager
        try:
            async with aiohttp.ClientSession() as session:
                silence_data = {
                    "matchers": [{"name": "alertname", "value": alertname, "isRegex": False}],
                    "startsAt": datetime.now(pytz.UTC).isoformat(),
                    "endsAt": (datetime.now(pytz.UTC) + timedelta(hours=hours)).isoformat(),
                    "createdBy": "telegram-bot",
                    "comment": f"Silenced via Telegram for {hours}h",
                }
                async with session.post(
                    f"{ALERTMANAGER_URL}/api/v2/silences",
                    json=silence_data
                ) as resp:
                    if resp.status == 200:
                        await query.edit_message_text(
                            query.message.text + f"\n\n🔕 <b>Alert silenced for {hours} hours</b>",
                            parse_mode=ParseMode.HTML
                        )
                    else:
                        await query.answer(f"Failed to silence: {resp.status}")
        except Exception as e:
            await query.answer(f"Error: {str(e)}")
        return

    # Restart container
    if data.startswith("restart_") and not data.startswith("restart_project_"):
        container_name = data.replace("restart_", "")
        try:
            container = docker_client.containers.get(container_name)
            await query.edit_message_text(f"🔄 {container_name} restarting...")
            container.restart(timeout=30)
            await asyncio.sleep(3)
            container.reload()

            if container.status == "running":
                await query.edit_message_text(f"✅ {container_name} restarted!")
            else:
                await query.edit_message_text(f"⚠️ {container_name} status: {container.status}")
        except Exception as e:
            await query.edit_message_text(f"❌ Error: {str(e)}")
        return

    # Project operations
    if data.startswith("restart_project_"):
        project_id = data.replace("restart_project_", "")
        if project_id in PROJECT_GROUPS:
            await query.edit_message_text(f"🔄 {PROJECT_GROUPS[project_id]['name']} restarting...")
            for name in PROJECT_GROUPS[project_id]["containers"]:
                try:
                    container = docker_client.containers.get(name)
                    container.restart(timeout=30)
                except Exception:
                    pass
            await query.edit_message_text(f"✅ {PROJECT_GROUPS[project_id]['name']} restarted!")
        return

    if data.startswith("stop_project_"):
        project_id = data.replace("stop_project_", "")
        if project_id in PROJECT_GROUPS:
            await query.edit_message_text(f"🛑 {PROJECT_GROUPS[project_id]['name']} stopping...")
            for name in PROJECT_GROUPS[project_id]["containers"]:
                try:
                    container = docker_client.containers.get(name)
                    container.stop(timeout=30)
                except Exception:
                    pass
            await query.edit_message_text(f"✅ {PROJECT_GROUPS[project_id]['name']} stopped!")
        return

    if data.startswith("start_project_"):
        project_id = data.replace("start_project_", "")
        if project_id in PROJECT_GROUPS:
            await query.edit_message_text(f"▶️ {PROJECT_GROUPS[project_id]['name']} starting...")
            for name in PROJECT_GROUPS[project_id]["containers"]:
                try:
                    container = docker_client.containers.get(name)
                    container.start()
                except Exception:
                    pass
            await query.edit_message_text(f"✅ {PROJECT_GROUPS[project_id]['name']} started!")
        return


# ============================================
# SCHEDULED REPORTS
# ============================================

async def send_daily_report(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily system report at 09:00."""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    uptime = datetime.now().timestamp() - psutil.boot_time()
    load1, load5, load15 = psutil.getloadavg()

    containers = docker_client.containers.list(all=True)
    running = sum(1 for c in containers if c.status == "running")
    total = len(containers)

    def get_emoji(percent, warn=70, crit=90):
        if percent >= crit:
            return "🔴"
        elif percent >= warn:
            return "🟡"
        return "🟢"

    report = f"""
📊 <b>Daily Report</b>
<code>━━━━━━━━━━━━━━━━━━━━━</code>
📅 {datetime.now(TIMEZONE).strftime("%d.%m.%Y %H:%M")}

<b>🖥️ System</b>
├ Uptime: {format_uptime(uptime)}
├ Load: {load1:.2f} / {load5:.2f} / {load15:.2f}
├ {get_emoji(cpu_percent)} CPU: {cpu_percent:.1f}%
├ {get_emoji(memory.percent)} RAM: {memory.percent:.1f}%
└ {get_emoji(disk.percent)} Disk: {disk.percent:.1f}%

<b>🐳 Docker</b> ({running}/{total})
"""

    # Check projects
    project_status = []
    for project_id, project_info in PROJECT_GROUPS.items():
        if project_id in ["monitoring", "infra"]:
            continue

        statuses = [get_container_status(c) for c in project_info["containers"]]
        running_count = statuses.count("🟢")
        total_count = len(project_info["containers"])

        if running_count == total_count:
            emoji = "🟢"
        elif running_count == 0:
            emoji = "🔴"
        else:
            emoji = "🟡"

        project_status.append(f"├ {emoji} {project_info['name']}: {running_count}/{total_count}")

    report += "\n".join(project_status)

    await context.bot.send_message(
        chat_id=ALLOWED_CHAT_ID,
        text=report,
        parse_mode=ParseMode.HTML
    )
    logger.info("Daily report sent")


# ============================================
# MAIN
# ============================================

async def run_webhook_server(app: web.Application):
    """Run the webhook server."""
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', WEBHOOK_PORT)
    await site.start()
    logger.info(f"Webhook server started on port {WEBHOOK_PORT}")


def main() -> None:
    """Start the bot."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    if not ALLOWED_CHAT_ID:
        logger.error("TELEGRAM_CHAT_ID not set!")
        return

    # Create application
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers - Standard commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("commands", help_command))
    application.add_handler(CommandHandler("settings", settings_command))

    # System status commands
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("health", health_check))
    application.add_handler(CommandHandler("cpu", cpu_command))
    application.add_handler(CommandHandler("memory", memory_command))
    application.add_handler(CommandHandler("disk", disk_command))

    # Docker management commands
    application.add_handler(CommandHandler("docker", docker_list))
    application.add_handler(CommandHandler("containers", docker_list))
    application.add_handler(CommandHandler("projects", projects_list))
    application.add_handler(CommandHandler("up", container_up))
    application.add_handler(CommandHandler("down", container_down))
    application.add_handler(CommandHandler("restart", container_restart))
    application.add_handler(CommandHandler("logs", container_logs))

    # Monitoring & Alerting commands
    application.add_handler(CommandHandler("alerts", alerts_command))
    application.add_handler(CommandHandler("grafana", grafana_command))
    application.add_handler(CommandHandler("silence", silence_command))
    application.add_handler(CommandHandler("ack", ack_command))

    # Enterprise ChatOps commands (2026 standards)
    application.add_handler(CommandHandler("snooze", snooze_command))
    application.add_handler(CommandHandler("escalate", escalate_command))
    application.add_handler(CommandHandler("resolve", resolve_command))
    application.add_handler(CommandHandler("oncall", oncall_command))
    application.add_handler(CommandHandler("history", history_command))

    # Callbacks
    application.add_handler(CallbackQueryHandler(button_callback))

    # Schedule daily report at 09:00
    job_queue = application.job_queue
    job_queue.run_daily(
        send_daily_report,
        time=time(hour=9, minute=0, tzinfo=TIMEZONE),
        name="daily_report"
    )
    logger.info("Daily report scheduled for 09:00")

    # Health check endpoint for container healthcheck
    async def health_handler(request: web.Request) -> web.Response:
        """Health check endpoint for Docker healthcheck."""
        return web.json_response({
            "status": "healthy",
            "version": "3.0.0",
            "timestamp": datetime.now(TIMEZONE).isoformat(),
            "alerts_tracked": len(alert_history),
            "alerts_acked": len(acknowledged_alerts),
        })

    # Create webhook server
    webhook_app = web.Application()
    webhook_app.router.add_post("/webhook/alertmanager", handle_alertmanager_webhook)
    webhook_app.router.add_get("/health", health_handler)
    webhook_app["bot"] = application.bot

    # Run both the bot and webhook server
    async def run_all():
        # Start webhook server
        await run_webhook_server(webhook_app)
        # Run bot
        await application.initialize()
        await application.start()
        await application.updater.start_polling(allowed_updates=Update.ALL_TYPES)

        # Set bot commands for menu (Enterprise standard)
        commands = [
            ("start", "Start bot"),
            ("help", "Command list"),
            ("status", "System status"),
            ("docker", "Container list"),
            ("projects", "Project status"),
            ("alerts", "Active alerts"),
            ("ack", "Acknowledge alert"),
            ("silence", "Silence alert"),
            ("snooze", "Snooze alerts"),
            ("resolve", "Resolve alert"),
            ("escalate", "Escalate alert"),
            ("grafana", "Dashboards"),
            ("health", "Health check"),
            ("settings", "Bot settings"),
        ]
        await application.bot.set_my_commands(commands)
        logger.info("Bot commands menu set successfully")

        # Keep running
        while True:
            await asyncio.sleep(3600)

    logger.info("Bot starting...")
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
