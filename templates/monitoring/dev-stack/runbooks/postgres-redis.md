# PostgreSQL & Redis - Runbook

## Alerts Covered
- PostgreSQLDown
- RedisDown
- PostgreSQLYuksekBaglanti
- PostgreSQLKritikBaglanti
- RedisYuksekBellek
- RedisKritikBellek

---

## PostgreSQL Issues

### Alert: PostgreSQLDown

#### Diagnosis

1. **Check container status**
```bash
docker ps -a | grep postgres
```

2. **Check logs**
```bash
docker logs <postgres-container> --tail 100
```

3. **Check disk space** (PostgreSQL stops if disk full)
```bash
df -h
du -sh /var/lib/docker/volumes/*postgres*
```

#### Resolution

```bash
# Restart PostgreSQL
docker restart <postgres-container>

# If container won't start, check data integrity
docker logs <postgres-container> 2>&1 | grep -i "error\|fatal"
```

### Alert: PostgreSQLYuksekBaglanti / PostgreSQLKritikBaglanti

#### Diagnosis

1. **Check current connections**
```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "SELECT count(*) FROM pg_stat_activity;"
```

2. **Check connection sources**
```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "SELECT client_addr, usename, state, count(*) FROM pg_stat_activity GROUP BY 1, 2, 3 ORDER BY 4 DESC;"
```

3. **Check for idle connections**
```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle';"
```

#### Resolution

1. **Kill idle connections**
```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE state = 'idle' AND pid <> pg_backend_pid();"
```

2. **Increase max_connections** (if needed)
```bash
# In docker-compose.yml
command: postgres -c max_connections=200
```

3. **Fix application connection pooling**
- Check Laravel/NestJS connection pool settings
- Ensure connections are being released properly

### Alert: PostgreSQLDusukCacheHitRatio

#### Diagnosis

```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "SELECT sum(blks_hit)::float / (sum(blks_hit) + sum(blks_read)) as cache_hit_ratio FROM pg_stat_database;"
```

#### Resolution

Increase shared_buffers:
```bash
# In docker-compose.yml
command: postgres -c shared_buffers=256MB
```

---

## Redis Issues

### Alert: RedisDown

#### Diagnosis

1. **Check container status**
```bash
docker ps -a | grep redis
```

2. **Check logs**
```bash
docker logs <redis-container> --tail 100
```

3. **Test connectivity**
```bash
docker exec <redis-container> redis-cli ping
```

#### Resolution

```bash
# Restart Redis
docker restart <redis-container>

# If data persistence issues
docker exec <redis-container> redis-cli DEBUG SLEEP 0
```

### Alert: RedisYuksekBellek / RedisKritikBellek

#### Diagnosis

1. **Check memory usage**
```bash
docker exec <redis-container> redis-cli INFO memory | grep -E "used_memory_human|maxmemory_human|maxmemory_policy"
```

2. **Check key count and sizes**
```bash
docker exec <redis-container> redis-cli INFO keyspace
docker exec <redis-container> redis-cli DBSIZE
```

3. **Find large keys**
```bash
docker exec <redis-container> redis-cli --bigkeys
```

#### Resolution

1. **If no maxmemory set, add it**
```yaml
# In docker-compose.yml
command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
```

2. **Clear expired keys manually**
```bash
docker exec <redis-container> redis-cli SCAN 0 COUNT 1000
# Then delete specific keys if needed
```

3. **Flush specific database** (CAUTION)
```bash
docker exec <redis-container> redis-cli FLUSHDB
```

### Alert: RedisYuksekBaglantiSayisi

#### Diagnosis

```bash
docker exec <redis-container> redis-cli CLIENT LIST | wc -l
docker exec <redis-container> redis-cli INFO clients
```

#### Resolution

1. **Kill idle connections**
```bash
docker exec <redis-container> redis-cli CLIENT KILL TYPE normal
```

2. **Increase maxclients**
```yaml
command: redis-server --maxclients 200
```

### Alert: RedisRejectedConnections

#### Resolution

Increase maxclients and check for connection leaks:
```yaml
command: redis-server --maxclients 1000 --timeout 300
```

---

## Maintenance Tasks

### PostgreSQL Backup
```bash
docker exec <postgres-container> pg_dump -U <user> <database> > backup.sql
```

### PostgreSQL Vacuum
```bash
docker exec <postgres-container> psql -U <user> -d <database> -c "VACUUM ANALYZE;"
```

### Redis Backup
```bash
docker exec <redis-container> redis-cli BGSAVE
docker cp <redis-container>:/data/dump.rdb ./redis-backup.rdb
```

### Check Replication (if applicable)
```bash
# PostgreSQL
docker exec <postgres-container> psql -U <user> -c "SELECT * FROM pg_stat_replication;"

# Redis
docker exec <redis-container> redis-cli INFO replication
```

---

## Prevention

### PostgreSQL Best Practices
1. Set `max_connections` appropriately
2. Use connection pooling (PgBouncer or app-level)
3. Monitor slow queries
4. Schedule regular VACUUM ANALYZE

### Redis Best Practices
1. Always set `maxmemory` and `maxmemory-policy`
2. Use appropriate data structures
3. Set key expiration times
4. Enable persistence (AOF or RDB)

---

## Escalation

If database issues persist:
1. Contact on-call DBA
2. Check for disk issues
3. Consider scaling (read replicas, sharding)
4. Review application query patterns

### Dashboard
[Grafana Database Dashboard](https://grafana-dev.yourdomain.com/d/databases-detailed)
