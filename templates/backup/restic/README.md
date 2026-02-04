# Restic Backup - Automated Docker Volume Backups

Fast, secure, deduplicated backups with support for multiple backends (S3, B2, local, SFTP).

## Features

- Encrypted, deduplicated backups
- Multiple backend support (S3, B2, local, SFTP, REST)
- Automatic scheduling with Ofelia
- Docker volume backup
- Retention policy management
- ~50% less storage than plain backups

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env

# Generate repository password (SAVE THIS!)
openssl rand -base64 32
# Add to .env as RESTIC_PASSWORD
```

### 2. Choose Backend

#### Local Backup
```bash
RESTIC_REPOSITORY=/backups
LOCAL_BACKUP_PATH=/home/deploy/backups
```

#### AWS S3
```bash
RESTIC_REPOSITORY=s3:s3.amazonaws.com/my-bucket/restic
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

#### Backblaze B2
```bash
RESTIC_REPOSITORY=b2:my-bucket:restic
B2_ACCOUNT_ID=your_id
B2_ACCOUNT_KEY=your_key
```

### 3. Start Backup Service

```bash
# Start scheduler only (for automatic backups)
docker compose up -d scheduler

# Or run manual backup first
docker compose --profile backup run --rm restic /scripts/backup.sh
```

## Manual Operations

### Initialize Repository
```bash
docker compose --profile backup run --rm restic restic init
```

### Run Backup Now
```bash
docker compose --profile backup run --rm restic /scripts/backup.sh
```

### List Snapshots
```bash
docker compose --profile backup run --rm restic restic snapshots
```

### Restore
```bash
# List snapshots
docker compose --profile backup run --rm restic /scripts/restore.sh

# Restore latest snapshot
docker compose --profile backup run --rm \
  -e RESTORE_TARGET=/tmp/restore \
  restic /scripts/restore.sh latest

# Restore specific snapshot
docker compose --profile backup run --rm restic /scripts/restore.sh abc123
```

### Cleanup Old Backups
```bash
docker compose --profile backup run --rm restic /scripts/cleanup.sh
```

### Check Repository Integrity
```bash
docker compose --profile backup run --rm restic restic check
```

### View Stats
```bash
docker compose --profile backup run --rm restic restic stats
```

## Backup Schedule

Default schedule (configured in docker-compose.yml):
- **Daily backup**: 3:00 AM
- **Weekly cleanup**: Sunday 4:00 AM

Modify the cron expressions in the scheduler labels to change:
```yaml
labels:
  - "ofelia.job-exec.backup.schedule=0 3 * * *"    # Daily at 3 AM
  - "ofelia.job-exec.cleanup.schedule=0 4 * * 0"   # Sunday at 4 AM
```

## Retention Policy

Default retention (in cleanup.sh):
- Keep last 7 snapshots
- Keep 7 daily snapshots
- Keep 4 weekly snapshots
- Keep 6 monthly snapshots
- Keep 2 yearly snapshots

Override via environment:
```bash
KEEP_LAST=10
KEEP_DAILY=14
KEEP_WEEKLY=8
KEEP_MONTHLY=12
KEEP_YEARLY=5
```

## Stopping Containers During Backup

For consistent database backups, stop containers:

```bash
# In .env
STOP_CONTAINERS=true
CONTAINERS_TO_STOP="postgres mysql vaultwarden"
```

## What Gets Backed Up

By default, all Docker volumes are backed up from:
```
/var/lib/docker/volumes/
```

Excluded patterns:
- `*.tmp`
- `*.log`
- `*.cache`
- `.git` directories

## Restore Specific Volume

```bash
# 1. Find the snapshot
docker compose --profile backup run --rm restic restic snapshots

# 2. Stop the container using the volume
docker stop mycontainer

# 3. Restore the volume
docker compose --profile backup run --rm \
  -e RESTORE_TARGET=/tmp/restore \
  restic /scripts/restore.sh abc123 myvolume_name

# 4. Copy data back to volume
docker cp restic:/tmp/restore/volumes/myvolume_name/_data/. \
  /var/lib/docker/volumes/myvolume_name/_data/

# 5. Restart container
docker start mycontainer
```

## Monitoring

Check backup logs:
```bash
docker logs restic-scheduler -f
```

Verify backups exist:
```bash
docker compose --profile backup run --rm restic restic snapshots --last 5
```

## Security Notes

1. **Store password securely**: Losing `RESTIC_PASSWORD` means losing access to backups
2. **Test restores**: Regularly verify backups can be restored
3. **Offsite backups**: Use S3/B2 for geographic redundancy
4. **Encrypt .env**: Consider GPG-encrypting your .env file

## Troubleshooting

### Repository not initialized
```bash
docker compose --profile backup run --rm restic restic init
```

### Permission denied on volumes
Ensure the container has access to `/var/lib/docker/volumes`:
```bash
ls -la /var/lib/docker/volumes/
```

### Check repository health
```bash
docker compose --profile backup run --rm restic restic check --read-data
```

## Resources

- [Restic Documentation](https://restic.readthedocs.io/)
- [Restic Backends](https://restic.readthedocs.io/en/latest/030_preparing_a_new_repo.html)
- [Ofelia Scheduler](https://github.com/mcuadros/ofelia)
