# Security Hardening

Essential security configurations for your VPS.

## 1. SSH Hardening

Edit `/etc/ssh/sshd_config`:

```bash
# Disable root login
PermitRootLogin no

# Disable password authentication (use SSH keys only)
PasswordAuthentication no

# Limit SSH to specific users
AllowUsers deploy

# Change default port (optional)
Port 2222
```

Restart SSH:
```bash
sudo systemctl restart sshd
```

## 2. Firewall (UFW)

```bash
# Install UFW
sudo apt install ufw

# Default policies
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Allow SSH (use your port if changed)
sudo ufw allow 22/tcp

# Allow HTTP/HTTPS for Traefik
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Enable firewall
sudo ufw enable

# Check status
sudo ufw status verbose
```

## 3. Fail2Ban

```bash
# Install
sudo apt install fail2ban

# Create local config
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
```

Edit `/etc/fail2ban/jail.local`:

```ini
[sshd]
enabled = true
port = ssh
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600
findtime = 600
```

```bash
# Restart and enable
sudo systemctl restart fail2ban
sudo systemctl enable fail2ban

# Check banned IPs
sudo fail2ban-client status sshd
```

## 4. Automatic Security Updates

```bash
# Install unattended-upgrades
sudo apt install unattended-upgrades

# Enable automatic updates
sudo dpkg-reconfigure -plow unattended-upgrades
```

## 5. Docker Security

### Limit Container Resources

Always set memory limits in docker-compose:

```yaml
services:
  app:
    mem_limit: 512m
    mem_reservation: 128m
```

### Use Non-Root User

In Dockerfile:
```dockerfile
RUN adduser --disabled-password --gecos '' appuser
USER appuser
```

### Read-Only Root Filesystem (where possible)

```yaml
services:
  app:
    read_only: true
    tmpfs:
      - /tmp
```

### Security Options

```yaml
services:
  app:
    security_opt:
      - no-new-privileges:true
```

## 6. Cloudflare Security

### Enable These Settings

- **SSL/TLS**: Full (strict) if using valid origin cert
- **Always Use HTTPS**: ON
- **Automatic HTTPS Rewrites**: ON
- **Minimum TLS Version**: 1.2
- **Opportunistic Encryption**: ON

### Firewall Rules

Block direct IP access (only allow Cloudflare IPs):
- [Cloudflare IP Ranges](https://www.cloudflare.com/ips/)

## 7. Basic Auth for Sensitive Services

For admin panels or monitoring dashboards:

```bash
# Generate password hash
docker run --rm httpd:alpine htpasswd -nb username 'password' | sed 's/\$/\$\$/g'
```

Add to Traefik labels:
```yaml
labels:
  - "traefik.http.routers.app.middlewares=app-auth"
  - "traefik.http.middlewares.app-auth.basicauth.users=username:$$apr1$$hash$$here"
```

## 8. Environment Variables Security

- Never commit `.env` files to git
- Use `.env.example` with placeholder values
- Set restrictive permissions: `chmod 600 .env`

## 9. Regular Maintenance

```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Update Docker images
docker compose pull
docker compose up -d

# Clean unused Docker resources
docker system prune -af

# Check for security updates
sudo apt list --upgradable
```

## Security Checklist

- [ ] SSH key authentication only
- [ ] Firewall configured (UFW)
- [ ] Fail2Ban installed
- [ ] Automatic updates enabled
- [ ] Docker resource limits set
- [ ] Cloudflare SSL configured
- [ ] Sensitive services protected with Basic Auth
- [ ] Environment files not in git
- [ ] Regular update schedule

## Next Steps

→ [Troubleshooting](troubleshooting.md)
