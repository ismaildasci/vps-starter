# Vaultwarden - Self-hosted Password Manager

Self-hosted Bitwarden-compatible server. Works with all official Bitwarden clients.

## Features

- Full Bitwarden API compatibility
- Official desktop, mobile, and browser extension support
- Organizations and sharing
- Emergency access
- Send (secure file/text sharing)
- Two-factor authentication
- WebSocket live sync
- Admin panel
- ~30MB RAM usage

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env

# Generate admin token
openssl rand -base64 48
# Add to .env as ADMIN_TOKEN
```

### 2. Update .env

```bash
# Required changes:
VAULTWARDEN_DOMAIN=https://vault.yourdomain.com
VAULTWARDEN_HOST=vault.yourdomain.com
ADMIN_TOKEN=your_generated_token
```

### 3. Start Vaultwarden

```bash
docker compose up -d
```

### 4. Create First Account

1. Navigate to `https://vault.yourdomain.com`
2. Click "Create Account"
3. After creating your account, disable signups in `.env`:
   ```
   SIGNUPS_ALLOWED=false
   ```
4. Restart: `docker compose up -d`

## Admin Panel

Access admin panel at: `https://vault.yourdomain.com/admin`

Use the `ADMIN_TOKEN` to login.

From admin panel you can:
- Invite users
- View all users
- Delete users
- View organizations
- Check diagnostics

## Client Setup

### Browser Extensions
1. Install Bitwarden extension
2. Click settings (gear icon)
3. Set "Self-hosted Environment" to: `https://vault.yourdomain.com`

### Desktop Apps
1. Before login, click "Self-hosted"
2. Enter server URL: `https://vault.yourdomain.com`

### Mobile Apps
1. Tap "Self-hosted"
2. Enter server URL: `https://vault.yourdomain.com`

## SMTP Configuration

For email features (account verification, password hints, emergency access):

```bash
SMTP_HOST=smtp.example.com
SMTP_FROM=vault@example.com
SMTP_PORT=587
SMTP_SECURITY=starttls
SMTP_USERNAME=vault@example.com
SMTP_PASSWORD=your_password
```

## Security Recommendations

1. **Disable signups** after creating your account
2. **Enable 2FA** for all users
3. **Use strong master password** (20+ characters)
4. **Regular backups** of the data volume
5. **Protect admin panel** with additional auth (Authelia)

## Protecting with Authelia

Add to docker-compose labels:
```yaml
labels:
  - "traefik.http.routers.vaultwarden.middlewares=authelia@file,secure@file"
```

Note: This adds an extra login layer before Vaultwarden.

## Backup

### Manual Backup
```bash
# Stop container (optional, for consistency)
docker stop vaultwarden

# Backup data volume
docker run --rm -v vaultwarden_data:/data -v $(pwd):/backup alpine \
  tar -czf /backup/vaultwarden-backup.tar.gz /data

# Restart
docker start vaultwarden
```

### Automated Backup (with Restic)
See `templates/backup/restic/` for automated backup solution.

### Important Files
- `/data/db.sqlite3` - All passwords and data
- `/data/config.json` - Server configuration
- `/data/attachments/` - File attachments
- `/data/sends/` - Secure sends

## Restore

```bash
# Stop container
docker stop vaultwarden

# Restore from backup
docker run --rm -v vaultwarden_data:/data -v $(pwd):/backup alpine \
  sh -c "cd /data && tar -xzf /backup/vaultwarden-backup.tar.gz --strip-components=1"

# Start container
docker start vaultwarden
```

## Troubleshooting

### Check logs
```bash
docker logs vaultwarden -f
```

### WebSocket not working
Ensure the WebSocket router is configured in Traefik labels.

### Can't access admin panel
Verify `ADMIN_TOKEN` is set in `.env` and container is restarted.

### Sync issues
Clear browser cache and try logging out/in.

## Resources

- [Vaultwarden Wiki](https://github.com/dani-garcia/vaultwarden/wiki)
- [Bitwarden Help Center](https://bitwarden.com/help/)
- [Vaultwarden GitHub](https://github.com/dani-garcia/vaultwarden)
