# Stirling PDF - Self-hosted PDF Tools

Privacy-first PDF manipulation with 50+ operations. No data leaves your server.

## Features

### Document Operations
- Merge / Split PDFs
- Rotate / Rearrange pages
- Add / Remove pages
- Extract pages

### Conversion
- PDF to Images (PNG, JPG)
- Images to PDF
- PDF to Word/Excel/PowerPoint
- HTML to PDF
- Markdown to PDF

### Security
- Add / Remove password protection
- Add watermarks
- Redact text
- Sanitize PDFs

### OCR & Text
- OCR (text recognition)
- Extract text
- Add text/annotations
- Auto-rename from content

### Advanced
- Compress PDFs
- Repair damaged PDFs
- Compare documents
- PDF/A conversion
- Flatten forms

## Quick Start

### 1. Configure Environment

```bash
cp .env.example .env
# Edit .env with your domain
```

### 2. Start Stirling PDF

```bash
docker compose up -d
```

### 3. Access

Navigate to `https://pdf.yourdomain.com`

## Authentication

### No Authentication (Default)
Best when protected by Authelia or VPN:
```bash
DOCKER_ENABLE_SECURITY=false
SECURITY_ENABLE_LOGIN=false
```

### Built-in Authentication
```bash
DOCKER_ENABLE_SECURITY=true
SECURITY_ENABLE_LOGIN=true
ADMIN_USERNAME=admin
ADMIN_PASSWORD=your_secure_password
```

### With Authelia (Recommended)
Add Authelia middleware to Traefik labels:
```yaml
labels:
  - "traefik.http.routers.stirling-pdf.middlewares=authelia@file,secure@file"
```

## OCR Languages

Additional OCR languages are downloaded automatically on first use.

Pre-install specific languages by creating a custom Dockerfile:
```dockerfile
FROM frooodle/s-pdf:latest
RUN apt-get update && apt-get install -y \
    tesseract-ocr-deu \
    tesseract-ocr-fra \
    tesseract-ocr-spa
```

## API Access

Stirling PDF provides a REST API for automation:

```bash
# Get available operations
curl https://pdf.yourdomain.com/api/v1/info/status

# Merge PDFs
curl -X POST https://pdf.yourdomain.com/api/v1/general/merge-pdfs \
  -F "fileInput=@file1.pdf" \
  -F "fileInput=@file2.pdf" \
  -o merged.pdf
```

API documentation: `https://pdf.yourdomain.com/swagger-ui/index.html`

## Performance

For large PDFs or OCR operations:
```yaml
# Increase resources in docker-compose.yml
mem_limit: 2g
cpus: 4
```

## Backup

No persistent data stored by default. If using authentication:
```bash
docker run --rm -v stirling_configs:/data -v $(pwd):/backup alpine \
  tar -czf /backup/stirling-configs.tar.gz /data
```

## Troubleshooting

### Check logs
```bash
docker logs stirling-pdf -f
```

### OCR not working
Ensure the language pack is installed. First OCR use downloads packs automatically.

### Out of memory on large files
Increase `mem_limit` in docker-compose.yml.

### PDF conversion fails
Some conversions require LibreOffice. The full image includes all dependencies.

## Resources

- [Stirling PDF GitHub](https://github.com/Stirling-Tools/Stirling-PDF)
- [API Documentation](https://stirlingtools.com/docs)
