# Ollama

Run large language models locally on your VPS.

## Why Ollama?

- **Privacy**: Your data never leaves your server
- **No API costs**: Run unlimited queries
- **Open models**: Llama 3, Mistral, Phi, Gemma, and more
- **Simple API**: OpenAI-compatible endpoint

## Quick Start

### CPU Version

```bash
docker compose up -d
```

### GPU Version (NVIDIA)

1. Install NVIDIA Container Toolkit:
```bash
# Ubuntu/Debian
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg
curl -s -L https://nvidia.github.io/libnvidia-container/stable/deb/nvidia-container-toolkit.list | \
  sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
  sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list
sudo apt-get update && sudo apt-get install -y nvidia-container-toolkit
sudo nvidia-ctk runtime configure --runtime=docker
sudo systemctl restart docker
```

2. Start with GPU support:
```bash
docker compose -f docker-compose.gpu.yml up -d
```

## Download Models

```bash
# Pull a model
docker exec ollama ollama pull llama3.2

# List available models
docker exec ollama ollama list

# Popular models:
# - llama3.2 (3B) - Fast, general purpose
# - llama3.1 (8B) - Better quality, needs more RAM
# - mistral (7B) - Good balance of speed and quality
# - phi3 (3.8B) - Microsoft's small but capable model
# - gemma2 (9B) - Google's open model
# - codellama (7B) - Optimized for code
```

## Model Recommendations by VPS RAM

| RAM | Recommended Models |
|-----|-------------------|
| 4GB | phi3:mini, gemma2:2b |
| 8GB | llama3.2, mistral:7b-instruct-q4_0 |
| 16GB | llama3.1:8b, codellama:13b |
| 32GB+ | llama3.1:70b-q4_0, mixtral |

## API Usage

Ollama exposes an OpenAI-compatible API on port 11434.

### Generate Text
```bash
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.2",
  "prompt": "Why is the sky blue?"
}'
```

### Chat
```bash
curl http://localhost:11434/api/chat -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Hello!"}]
}'
```

### OpenAI-Compatible Endpoint
```bash
curl http://localhost:11434/v1/chat/completions -d '{
  "model": "llama3.2",
  "messages": [{"role": "user", "content": "Hello!"}]
}'
```

## Integration with Open WebUI

Ollama works seamlessly with Open WebUI (see `templates/ai/open-webui/`):

```yaml
# Both services share the 'web' network
# Open WebUI connects to: http://ollama:11434
```

## Resource Tuning

Edit `.env` to adjust resources:

```bash
# For larger models
OLLAMA_MEM_LIMIT=8g
OLLAMA_MEM_RESERVATION=4g
OLLAMA_CPUS=4
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `OLLAMA_ORIGINS` | CORS allowed origins | `*` |
| `OLLAMA_MEM_LIMIT` | Memory limit | `4g` |
| `OLLAMA_MEM_RESERVATION` | Memory reservation | `2g` |
| `OLLAMA_CPUS` | CPU limit | `2` |
| `OLLAMA_TRAEFIK_ENABLE` | Expose via Traefik | `false` |
| `OLLAMA_DOMAIN` | Traefik domain | `ollama.example.com` |

## Troubleshooting

### Out of memory
```bash
# Try a smaller model or quantized version
docker exec ollama ollama pull llama3.2:1b
docker exec ollama ollama pull mistral:7b-instruct-q4_0
```

### Check GPU usage
```bash
nvidia-smi
docker exec ollama ollama ps  # Shows loaded models
```

### View logs
```bash
docker logs ollama
```

### Model download stuck
```bash
# Check disk space
df -h
# Ollama models are stored in the volume
docker volume inspect ollama_data
```

## Security Notes

- API is exposed only on localhost by default
- Enable Traefik only if you need remote access
- Use basic auth or VPN for production API access
- Consider Tailscale for private access
