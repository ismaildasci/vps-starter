# HashiCorp Vault

Secure secret management for your infrastructure.

## Quick Start

1. Start Vault:
```bash
docker compose up -d
```

2. Initialize Vault (first time only):
```bash
docker exec -it vault vault operator init
```
**IMPORTANT:** Save the unseal keys and root token securely!

3. Unseal Vault:
```bash
docker exec -it vault vault operator unseal <key1>
docker exec -it vault vault operator unseal <key2>
docker exec -it vault vault operator unseal <key3>
```

4. Login:
```bash
docker exec -it vault vault login <root-token>
```

5. Enable secrets engine:
```bash
docker exec -it vault vault secrets enable -path=secret kv-v2
```

6. Create a secret:
```bash
docker exec -it vault vault kv put secret/apps/myapp \
  username=admin \
  password=secret123
```

## Using Policies

Apply the apps policy:
```bash
docker exec -it vault vault policy write apps /vault/policies/apps-policy.hcl
```

Create an AppRole for applications:
```bash
docker exec -it vault vault auth enable approle
docker exec -it vault vault write auth/approle/role/myapp \
  policies=apps \
  token_ttl=1h \
  token_max_ttl=4h
```

## Environment Variables

- `VAULT_DOMAIN`: Domain for Vault UI (default: vault.example.com)
- `VAULT_ADDR`: Internal Vault address (set automatically)

## Security Notes

- In production, enable TLS in vault.hcl
- Never commit unseal keys or root tokens
- Use AppRole or other auth methods for applications
- Regularly rotate secrets and tokens
