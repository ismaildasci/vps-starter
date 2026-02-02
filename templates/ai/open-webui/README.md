# Open WebUI

Beautiful ChatGPT-like interface for Ollama and OpenAI-compatible APIs.

## Features

- **Chat interface**: Familiar ChatGPT-style UI
- **Multi-model**: Switch between models in conversations
- **User management**: Built-in authentication and roles
- **Conversation history**: Persistent chat history
- **RAG support**: Upload documents for context
- **Custom prompts**: Save and share system prompts

## Prerequisites

Ollama must be running on the same Docker network:

```bash
# Start Ollama first
cd ../ollama
docker compose up -d

# Download at least one model
docker exec ollama ollama pull llama3.2
```

## Quick Start

1. Configure environment:
```bash
cp .env.example .env

# Generate a secret key
echo "WEBUI_SECRET_KEY=$(openssl rand -hex 32)" >> .env

# Set your domain
# Edit .env: WEBUI_DOMAIN=chat.yourdomain.com
```

2. Start Open WebUI:
```bash
docker compose up -d
```

3. Access the UI:
   - URL: `https://chat.yourdomain.com`
   - Create admin account on first visit

## First-Time Setup

1. Open `https://chat.yourdomain.com`
2. Click "Sign up" to create admin account
3. After creating admin, disable signup in `.env`:
   ```bash
   ENABLE_SIGNUP=false
   docker compose up -d  # Restart to apply
   ```

## User Management

### Roles
- **Admin**: Full access, can manage users and settings
- **User**: Can chat and manage own conversations
- **Pending**: Awaits admin approval

### Adding Users
As admin:
1. Go to Settings > Admin Panel
2. Add users manually, or
3. Enable signup temporarily

## Model Configuration

Models are pulled from Ollama automatically. To manage:

1. Pull new models:
```bash
docker exec ollama ollama pull mistral
docker exec ollama ollama pull codellama
```

2. Refresh in Open WebUI:
   - Models appear automatically
   - Use the dropdown to switch models

## Hybrid Setup (Ollama + OpenAI)

Use both local and cloud models:

```bash
# In .env
ENABLE_OLLAMA_API=true
ENABLE_OPENAI_API=true
OPENAI_API_KEY=sk-xxxxx
```

This enables:
- Local models via Ollama (free, private)
- GPT-4/Claude via OpenAI API (paid, more capable)

## RAG (Document Chat)

Upload documents to chat with them:

1. In a conversation, click the attachment icon
2. Upload PDF, TXT, MD, or other documents
3. Ask questions about the document

Documents are processed locally using the configured embedding model.

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_BASE_URL` | Ollama API endpoint | `http://ollama:11434` |
| `WEBUI_SECRET_KEY` | Session encryption key | Random |
| `WEBUI_AUTH` | Enable authentication | `true` |
| `ENABLE_SIGNUP` | Allow new registrations | `false` |
| `DEFAULT_USER_ROLE` | Role for new users | `user` |
| `ENABLE_OLLAMA_API` | Enable Ollama backend | `true` |
| `ENABLE_OPENAI_API` | Enable OpenAI backend | `false` |
| `OPENAI_API_KEY` | OpenAI API key | Empty |
| `WEBUI_DOMAIN` | Traefik domain | `chat.example.com` |

## Backup

Chat history is stored in the Docker volume:

```bash
# Backup
docker run --rm -v open-webui_open_webui_data:/data -v $(pwd):/backup alpine tar czf /backup/open-webui-backup.tar.gz /data

# Restore
docker run --rm -v open-webui_open_webui_data:/data -v $(pwd):/backup alpine tar xzf /backup/open-webui-backup.tar.gz -C /
```

## Troubleshooting

### Can't connect to Ollama
```bash
# Verify Ollama is running
docker ps | grep ollama

# Test connection from Open WebUI container
docker exec open-webui curl http://ollama:11434/api/tags
```

### No models available
```bash
# Pull models in Ollama
docker exec ollama ollama pull llama3.2

# Check models
docker exec ollama ollama list
```

### Forgot admin password
```bash
# Access the database
docker exec -it open-webui sqlite3 /app/backend/data/webui.db

# Reset password (set to 'password')
UPDATE user SET password = '$2b$12$...' WHERE role = 'admin';
```

### View logs
```bash
docker logs open-webui
```

## Security Notes

- Always set a strong `WEBUI_SECRET_KEY`
- Disable signup after creating admin account
- Use Traefik's `secure@file` middleware
- Consider Tailscale for private access
- Regularly backup conversation data
