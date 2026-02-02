# Tailscale

Zero Trust mesh VPN for private access to your services.

## Why Tailscale?

- **No port exposure**: Access internal services without public ports
- **Zero Trust**: Every connection is authenticated and encrypted
- **Simple**: No firewall rules, NAT traversal handled automatically
- **MagicDNS**: Access services by hostname (e.g., `vps-server.tailnet-name.ts.net`)

## Quick Start

1. Get an auth key from [Tailscale Admin Console](https://login.tailscale.com/admin/settings/keys)
   - Create a **reusable** key for servers
   - Enable "Ephemeral" if you want auto-cleanup on disconnect

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your auth key
```

3. Start Tailscale:
```bash
docker compose up -d
```

4. Verify connection:
```bash
docker exec tailscale tailscale status
```

## Use Cases

### Access Internal Services

Services on the `web` network are accessible via Tailscale IP:
```bash
# From any device on your Tailnet
curl http://100.x.x.x:3000  # Direct container access
```

### Subnet Router

Expose your entire Docker network to Tailscale:

1. Edit `.env`:
```bash
TS_ROUTES=172.18.0.0/16
```

2. Approve routes in Tailscale Admin Console:
   - Go to Machines > your-server > Edit route settings
   - Enable the advertised subnet

3. Access any container by its Docker IP from your Tailnet

### Exit Node

Route all traffic through your VPS:

1. Edit `.env`:
```bash
TS_EXTRA_ARGS=--advertise-exit-node
```

2. Approve in Tailscale Admin Console:
   - Go to Machines > your-server > Edit route settings
   - Enable "Use as exit node"

## Traefik Integration

For internal-only services, use Tailscale IP instead of public DNS:

```yaml
# In your service's docker-compose.yml
labels:
  - "traefik.http.routers.myservice.rule=Host(`myservice.local`)"
  # No TLS needed for internal traffic
```

Access via: `http://myservice.local` (add to `/etc/hosts` or use MagicDNS)

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TAILSCALE_AUTHKEY` | Auth key from Tailscale console | Required |
| `TAILSCALE_HOSTNAME` | Machine name in Tailscale | `vps-server` |
| `TS_USERSPACE` | Use userspace networking | `true` |
| `TS_ROUTES` | Subnets to advertise | Empty |
| `TS_EXTRA_ARGS` | Additional tailscale flags | Empty |

## Troubleshooting

### Check status
```bash
docker exec tailscale tailscale status
docker exec tailscale tailscale netcheck
```

### View logs
```bash
docker logs tailscale
```

### Re-authenticate
```bash
docker exec tailscale tailscale up --reset
```

## Security Notes

- Auth keys are sensitive - never commit `.env` files
- Use ACLs in Tailscale to restrict access between machines
- Consider enabling key expiry for additional security
