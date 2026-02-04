# Authelia - SSO and Multi-Factor Authentication

Lightweight identity provider for Single Sign-On (SSO) with Multi-Factor Authentication (MFA).

## Features

- Single Sign-On for all your services
- Multi-Factor Authentication (TOTP, WebAuthn/Passkeys)
- Native Traefik ForwardAuth integration
- File-based or LDAP authentication backend
- Access control policies per domain
- Brute force protection
- Password reset via email
- ~30MB RAM usage

## Quick Start

### 1. Generate Secrets

```bash
# Generate random secrets
openssl rand -hex 32  # JWT Secret
openssl rand -hex 32  # Session Secret
openssl rand -hex 32  # Storage Encryption Key
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your domain and secrets
```

### 3. Update Configuration

Edit `config/configuration.yml`:
- Replace `example.com` with your domain
- Configure access control rules
- (Optional) Enable SMTP for password reset

### 4. Add Users

Generate password hash:
```bash
docker run --rm authelia/authelia:latest authelia crypto hash generate argon2
# Enter password when prompted
```

Edit `config/users_database.yml`:
```yaml
users:
  admin:
    displayname: "Admin"
    password: "$argon2id$v=19$..." # Paste hash here
    email: admin@yourdomain.com
    groups:
      - admins
```

### 5. Start Authelia

```bash
docker compose up -d
```

### 6. Configure Traefik

Add to your Traefik's `dynamic.yml`:

```yaml
http:
  middlewares:
    authelia:
      forwardAuth:
        address: http://authelia:9091/api/verify?rd=https://auth.yourdomain.com
        trustForwardHeader: true
        authResponseHeaders:
          - Remote-User
          - Remote-Groups
          - Remote-Name
          - Remote-Email
```

## Protecting Services

Add middleware to any service's docker-compose labels:

```yaml
labels:
  - "traefik.http.routers.myapp.middlewares=authelia@file"
```

Or combine with secure middleware:
```yaml
labels:
  - "traefik.http.routers.myapp.middlewares=authelia@file,secure@file"
```

## Access Control Policies

In `configuration.yml`, configure policies per domain:

```yaml
access_control:
  default_policy: deny
  rules:
    # No auth required
    - domain: public.example.com
      policy: bypass

    # Username/password only
    - domain: app.example.com
      policy: one_factor

    # Requires 2FA
    - domain: admin.example.com
      policy: two_factor
```

## SMTP Configuration (Production)

For password reset functionality, uncomment and configure SMTP in `configuration.yml`:

```yaml
notifier:
  smtp:
    address: smtp://smtp.example.com:587
    sender: "Authelia <noreply@example.com>"
    username: noreply@example.com
    password: # Set via AUTHELIA_SMTP_PASSWORD env var
```

## 2FA Setup

1. Login to Authelia portal (https://auth.yourdomain.com)
2. Click "Register device"
3. Scan QR code with authenticator app (Google Authenticator, Authy, etc.)
4. Enter verification code

## Backup

Important files to backup:
- `config/users_database.yml` - User credentials
- `/data/db.sqlite3` - Session and 2FA data

```bash
docker exec authelia tar -czf - /data > authelia-backup.tar.gz
```

## Troubleshooting

### Check logs
```bash
docker logs authelia -f
```

### Verify configuration
```bash
docker exec authelia authelia validate-config
```

### Reset 2FA for a user
```bash
docker exec authelia authelia storage user totp delete --user admin
```

## Resources

- [Authelia Documentation](https://www.authelia.com/docs/)
- [Configuration Reference](https://www.authelia.com/configuration/)
- [Traefik Integration](https://www.authelia.com/integration/proxies/traefik/)
