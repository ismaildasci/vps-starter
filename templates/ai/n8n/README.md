# n8n

Powerful workflow automation with AI capabilities.

## Features

- **400+ integrations**: Connect to almost any service
- **AI nodes**: ChatGPT, Claude, Ollama, LangChain
- **Code nodes**: JavaScript/Python for custom logic
- **Self-hosted**: Full control over your data
- **Webhook triggers**: Build APIs and automations

## Quick Start

1. Configure environment:
```bash
cp .env.example .env

# Generate encryption key
echo "N8N_ENCRYPTION_KEY=$(openssl rand -hex 32)" >> .env

# Set your domain
# Edit .env: N8N_DOMAIN=n8n.yourdomain.com

# Set database password
# Edit .env: DB_POSTGRESDB_PASSWORD=secure-password
```

2. Start n8n:
```bash
docker compose up -d
```

3. Access the UI:
   - URL: `https://n8n.yourdomain.com`
   - Create account on first visit

## Use Cases

### AI Workflows

**Ollama Integration**:
```
n8n can connect to local Ollama for:
- Document summarization
- Content generation
- Data extraction
- Chatbots
```

Connect to Ollama using HTTP Request node:
- URL: `http://ollama:11434/api/generate`
- Method: POST

**OpenAI/Claude**:
- Use built-in OpenAI or Anthropic nodes
- Or LangChain nodes for advanced AI workflows

### Webhook Automation

Create APIs without code:
1. Add "Webhook" trigger node
2. Build your workflow
3. n8n generates a URL: `https://n8n.yourdomain.com/webhook/xxx`

### Scheduled Tasks

Cron-based automation:
1. Add "Schedule Trigger" node
2. Set your schedule (e.g., every hour, daily at 9am)
3. Automate reports, backups, notifications

### Example Workflows

**Daily Report to Telegram**:
```
Schedule Trigger -> HTTP Request (API) -> Code (process data) -> Telegram
```

**GitHub Issue to Discord**:
```
GitHub Trigger -> Discord (send message)
```

**AI Content Pipeline**:
```
RSS Trigger -> Ollama (summarize) -> Notion (save) -> Slack (notify)
```

## Integrations

Popular integrations available:
- **Communication**: Slack, Discord, Telegram, Email
- **Databases**: PostgreSQL, MySQL, MongoDB, Redis
- **Cloud**: AWS, GCP, Cloudflare
- **Dev Tools**: GitHub, GitLab, Jira, Linear
- **AI**: OpenAI, Anthropic, Ollama, HuggingFace
- **CRM**: Salesforce, HubSpot, Pipedrive
- **Productivity**: Notion, Airtable, Google Sheets

## Using with Ollama

For local AI workflows:

1. Ensure Ollama is running (see `templates/ai/ollama/`)
2. In n8n, use HTTP Request node:
   ```
   URL: http://ollama:11434/api/generate
   Method: POST
   Body:
   {
     "model": "llama3.2",
     "prompt": "{{ $json.text }}",
     "stream": false
   }
   ```

3. Or use the LangChain nodes with Ollama base URL

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `N8N_ENCRYPTION_KEY` | Encrypts credentials | Required |
| `N8N_DOMAIN` | Your n8n domain | `n8n.example.com` |
| `WEBHOOK_URL` | Public webhook URL | `https://n8n.example.com` |
| `DB_POSTGRESDB_PASSWORD` | Database password | `changeme` |
| `EXECUTIONS_DATA_PRUNE` | Auto-delete old executions | `true` |
| `EXECUTIONS_DATA_MAX_AGE` | Hours to keep executions | `168` |
| `GENERIC_TIMEZONE` | Timezone for schedules | `Europe/Istanbul` |

## Backup

### Workflows Only
```bash
# Export all workflows
docker exec n8n n8n export:workflow --all --output=/home/node/.n8n/backups/

# Copy from container
docker cp n8n:/home/node/.n8n/backups ./n8n-workflows-backup
```

### Full Backup (DB + Workflows)
```bash
# PostgreSQL
docker exec n8n-postgres pg_dump -U n8n n8n > n8n-db-backup.sql

# n8n data volume
docker run --rm -v n8n_n8n_data:/data -v $(pwd):/backup alpine tar czf /backup/n8n-data-backup.tar.gz /data
```

## Troubleshooting

### Can't access n8n
```bash
# Check container status
docker ps | grep n8n
docker logs n8n
```

### Database connection failed
```bash
# Check PostgreSQL
docker logs n8n-postgres
docker exec n8n-postgres pg_isready -U n8n
```

### Webhooks not working
- Ensure `WEBHOOK_URL` matches your public URL
- Check Traefik is routing correctly
- Verify firewall allows HTTPS

### Credentials not saving
- Ensure `N8N_ENCRYPTION_KEY` is set
- Key must remain constant - changing it breaks existing credentials

## Security Notes

- Always set a strong `N8N_ENCRYPTION_KEY` and `DB_POSTGRESDB_PASSWORD`
- Never expose n8n without authentication
- Use Traefik's `secure@file` middleware
- Regularly backup workflows and credentials
- Review workflow permissions for multi-user setups
