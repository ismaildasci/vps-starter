# Cloudflare Tunnel

Zero Trust access to your services without exposing ports.

## Why Cloudflare Tunnel?

- **No open ports**: All traffic goes through Cloudflare's network
- **Automatic SSL**: No certificate management needed
- **DDoS protection**: Cloudflare's network protects your origin
- **Access policies**: Add authentication without changing your apps
- **Free tier**: Available on Cloudflare's free plan

## Quick Start

### 1. Create Tunnel

1. Go to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/)
2. Navigate to **Networks > Tunnels**
3. Click **Create a tunnel**
4. Name your tunnel (e.g., `vps-server`)
5. Copy the tunnel token

### 2. Configure Environment

```bash
cp .env.example .env
# Paste your tunnel token in .env
```

### 3. Start Tunnel

```bash
docker compose up -d
```

### 4. Add Public Hostnames

In Cloudflare Zero Trust Dashboard:
1. Go to your tunnel > **Public Hostname**
2. Add hostnames for your services:

| Subdomain | Domain | Service | URL |
|-----------|--------|---------|-----|
| app | example.com | HTTP | http://myapp:3000 |
| grafana | example.com | HTTP | http://grafana:3000 |
| api | example.com | HTTP | http://api:8080 |

**Note**: Use container names as hostnames since cloudflared is on the same Docker network.

## Use Cases

### Expose Web Apps

Configure in Cloudflare Dashboard:
- Subdomain: `app`
- Domain: `example.com`
- Service: `HTTP`
- URL: `http://container-name:port`

Access via: `https://app.example.com`

### Private Services with Access Policies

1. In Zero Trust Dashboard, go to **Access > Applications**
2. Create an application
3. Set policies (email, IP, device posture, etc.)

Example: Require Google login for Grafana access.

### SSH Access

1. Add hostname:
   - Service: `SSH`
   - URL: `ssh://localhost:22`

2. Install cloudflared on your local machine
3. Connect: `cloudflared access ssh --hostname ssh.example.com`

### RDP/VNC Access

1. Add hostname:
   - Service: `RDP` or `TCP`
   - URL: `rdp://localhost:3389` or `tcp://localhost:5900`

2. Use cloudflared as a proxy on client side

## Comparison with Traefik

| Feature | Cloudflare Tunnel | Traefik |
|---------|------------------|---------|
| Port exposure | None required | 80, 443 |
| SSL management | Automatic | DNS challenge |
| DDoS protection | Built-in | None |
| Access policies | Built-in | Need external auth |
| Speed | Cloudflare CDN | Direct |

**Recommendation**: Use both together:
- Cloudflare Tunnel for public services needing extra protection
- Traefik for internal routing and services accessed via Tailscale

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `CLOUDFLARE_TUNNEL_TOKEN` | Tunnel token from dashboard | Required |

## Troubleshooting

### Check tunnel status
```bash
docker logs cloudflared
```

### Verify connectivity
Check tunnel status in Cloudflare Dashboard - should show "HEALTHY"

### Common issues

**Service unreachable**:
- Verify service is on the `web` network
- Check container name matches URL in dashboard
- Ensure service is running: `docker ps`

**Token issues**:
- Regenerate token in Cloudflare Dashboard
- Ensure no extra whitespace in `.env`

## Security Notes

- Tunnel tokens are sensitive - never commit `.env` files
- Use Access policies for sensitive services
- Enable audit logs in Zero Trust Dashboard
- Consider WAF rules for additional protection
