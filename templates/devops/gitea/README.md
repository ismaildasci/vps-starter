# Gitea - Self-hosted Git Server

Lightweight GitHub/GitLab alternative with CI/CD (Actions) and container registry support.

## Features

- Full Git hosting (repos, issues, PRs, wiki)
- Gitea Actions (GitHub Actions compatible CI/CD)
- Package/Container registry
- OAuth/OIDC authentication
- Git LFS support
- ~100MB RAM usage
- SQLite or PostgreSQL backend

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env

# Generate secrets
openssl rand -hex 32  # SECRET_KEY
openssl rand -hex 32  # INTERNAL_TOKEN
```

### 2. Update .env

```bash
GITEA_DOMAIN=git.yourdomain.com
GITEA_ROOT_URL=https://git.yourdomain.com
DB_PASSWORD=your_secure_password
SECRET_KEY=your_generated_secret
INTERNAL_TOKEN=your_generated_token
```

### 3. Start Gitea

```bash
docker compose up -d
```

### 4. Initial Setup

1. Navigate to `https://git.yourdomain.com`
2. Complete the installation wizard
3. Create admin account
4. Set `INSTALL_LOCK=true` in .env and restart

### 5. Disable Registration (Recommended)

After creating accounts:
```bash
# In .env
DISABLE_REGISTRATION=true
```
Then restart: `docker compose up -d`

## SSH Access

Configure SSH access for `git clone git@git.yourdomain.com:user/repo.git`:

### Option 1: Different Port (Recommended)
```bash
# Uses port 2222 by default
git clone ssh://git@git.yourdomain.com:2222/user/repo.git
```

Or add to `~/.ssh/config`:
```
Host git.yourdomain.com
  Port 2222
  User git
```

### Option 2: Same Port as System SSH
If using port 22, you need SSH passthrough on the host. See [Gitea docs](https://docs.gitea.io/en-us/install-with-docker/#ssh-container-passthrough).

## Gitea Actions (CI/CD)

### Enable Actions
```bash
ACTIONS_ENABLED=true
```

### Register a Runner

1. Go to Site Administration > Actions > Runners
2. Create new runner, copy registration token
3. Add to .env:
   ```bash
   RUNNER_TOKEN=your_registration_token
   ```
4. Start runner:
   ```bash
   docker compose --profile runner up -d
   ```

### Example Workflow
Create `.gitea/workflows/ci.yml` in your repo:

```yaml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run tests
        run: echo "Running tests..."
```

## Package Registry

Gitea includes registries for:
- Docker/OCI containers
- npm packages
- PyPI packages
- Maven artifacts
- NuGet packages
- Cargo crates

### Docker Registry Example
```bash
# Login
docker login git.yourdomain.com

# Tag and push
docker tag myimage git.yourdomain.com/user/myimage:latest
docker push git.yourdomain.com/user/myimage:latest
```

## OAuth/SSO Integration

### With Authelia
1. In Gitea: Site Administration > Authentication Sources
2. Add OAuth2 source
3. Configure with Authelia OIDC settings

### GitHub/GitLab Login
Add external OAuth providers in Authentication Sources.

## SMTP Configuration

For notifications and password reset:

```bash
MAILER_ENABLED=true
SMTP_ADDR=smtp.example.com
SMTP_PORT=587
SMTP_FROM=gitea@example.com
SMTP_USER=gitea@example.com
SMTP_PASSWORD=your_password
```

## Mirror Repositories

Gitea can mirror external repositories:

1. New Repository > New Migration
2. Enter source URL (GitHub, GitLab, etc.)
3. Enable "Mirror" for automatic sync

## Backup

### Gitea Data
```bash
# Stop gitea
docker stop gitea

# Backup volumes
docker run --rm -v gitea_data:/data -v $(pwd):/backup alpine \
  tar -czf /backup/gitea-data.tar.gz /data

# Backup database
docker exec gitea-postgres pg_dump -U gitea gitea > gitea-db.sql

# Restart
docker start gitea
```

### With Restic
Include these volumes in your Restic backup configuration:
- `gitea_data`
- `gitea_postgres_data`

## Troubleshooting

### Check logs
```bash
docker logs gitea -f
docker logs gitea-postgres -f
```

### Database connection issues
Ensure PostgreSQL is healthy:
```bash
docker exec gitea-postgres pg_isready -U gitea
```

### SSH not working
Check port mapping and firewall:
```bash
# Test SSH connection
ssh -T -p 2222 git@git.yourdomain.com
```

### Reset admin password
```bash
docker exec -it gitea gitea admin user change-password -u admin -p newpassword
```

## Resources

- [Gitea Documentation](https://docs.gitea.io/)
- [Gitea Actions](https://docs.gitea.io/en-us/actions/overview/)
- [Gitea Packages](https://docs.gitea.io/en-us/packages/overview/)
- [Gitea GitHub](https://github.com/go-gitea/gitea)
