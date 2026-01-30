# CrowdSec + Traefik Bouncer

Modern IPS (Intrusion Prevention System) - Fail2ban alternatifi.

## Özellikler

- Traefik log analizi
- Topluluk tabanlı IP blacklist paylaşımı
- HTTP CVE koruması
- SSH brute force koruması
- Fail2ban'dan 60x daha hızlı (Go vs Python)

## Kurulum

### 1. CrowdSec'i başlat

```bash
docker compose up -d
```

### 2. Bouncer key oluştur

```bash
docker exec crowdsec cscli bouncers add traefik-bouncer -o raw
```

### 3. Key'i .env'e ekle

```bash
echo "BOUNCER_KEY_TRAEFIK=<key>" > .env
```

### 4. Traefik'i yapılandır

`traefik.yml`'e ekle:

```yaml
experimental:
  plugins:
    crowdsec:
      moduleName: github.com/maxlerebourg/crowdsec-bouncer-traefik-plugin
      version: v1.3.5
```

`dynamic.yml`'e middleware ekle:

```yaml
http:
  middlewares:
    crowdsec:
      plugin:
        crowdsec:
          enabled: true
          crowdsecLapiHost: crowdsec:8080
          crowdsecLapiKey: <your-bouncer-key>
          crowdsecMode: live
```

### 5. Middleware'i router'lara ekle

```yaml
labels:
  - "traefik.http.routers.myapp.middlewares=crowdsec@file"
```

## Faydalı Komutlar

```bash
# Kararları listele
docker exec crowdsec cscli decisions list

# Metrikleri gör
docker exec crowdsec cscli metrics

# IP'yi manuel ban
docker exec crowdsec cscli decisions add --ip 1.2.3.4 --reason "manual ban"

# IP'yi unban
docker exec crowdsec cscli decisions delete --ip 1.2.3.4

# Alert'leri gör
docker exec crowdsec cscli alerts list

# Bouncer'ları listele
docker exec crowdsec cscli bouncers list
```

## Collections

Varsayılan olarak yüklenen koleksiyonlar:

- `crowdsecurity/traefik` - Traefik log parsing
- `crowdsecurity/http-cve` - HTTP CVE koruması
- `crowdsecurity/whitelist-good-actors` - Bilinen iyi IP'ler
- `crowdsecurity/linux` - Linux sistem logları
