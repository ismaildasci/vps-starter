# VPS Monitoring Telegram Bot - Enterprise Dockerfile
# Version: 3.0.0
# Optimized for production with security best practices

FROM python:3.12-alpine AS builder

WORKDIR /build

# Install build dependencies
RUN apk add --no-cache gcc musl-dev linux-headers python3-dev

# Install Python dependencies with pip cache
COPY requirements.txt .
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install --user -r requirements.txt

# Production image
FROM python:3.12-alpine

# Labels for container management
LABEL maintainer="Your Name"
LABEL version="3.0.0"
LABEL description="VPS Monitoring & Management Telegram Bot - Enterprise Edition"

# Install runtime dependencies and create user with docker group access
# GID 999 is the docker group on the host - use existing group or create
RUN apk add --no-cache curl tini && \
    adduser -D -u 1000 botuser && \
    addgroup -g 999 docker 2>/dev/null || true && \
    addgroup botuser $(getent group 999 | cut -d: -f1)

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /root/.local /home/botuser/.local

# Copy application
COPY --chown=botuser:botuser bot.py .

# Switch to non-root user
USER botuser

# Add Python user packages to PATH
ENV PATH="/home/botuser/.local/bin:$PATH"
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Health check endpoint
EXPOSE 5001

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5001/health || exit 1

# Use tini as init system for proper signal handling
ENTRYPOINT ["/sbin/tini", "--"]

# Run bot
CMD ["python", "-u", "bot.py"]
