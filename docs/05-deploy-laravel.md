# Deploy Laravel Application

Deploy Laravel 11/12 with Inertia.js + Vue using Docker and Traefik.

## 1. Project Structure

```
your-laravel-app/
├── Dockerfile
├── docker-compose.traefik.yml
├── docker/
│   ├── nginx.conf
│   ├── php.ini
│   └── supervisord.conf
├── .env
└── ... (your Laravel app files)
```

## 2. Dockerfile

```dockerfile
# Composer stage
FROM composer:2 AS composer
WORKDIR /app
COPY composer.json composer.lock ./
RUN composer install --no-dev --no-scripts --no-autoloader --ignore-platform-reqs
COPY . .
RUN composer dump-autoload --optimize --no-dev --no-scripts

# Node stage (for Vite assets)
FROM node:22-alpine AS node-builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY resources/ ./resources/
COPY vite.config.ts tsconfig.json tailwind.config.js postcss.config.js ./
COPY --from=composer /app/vendor ./vendor
RUN npm run build

# Production stage
FROM php:8.3-fpm-alpine

RUN apk add --no-cache \
    nginx supervisor libpng-dev libjpeg-turbo-dev freetype-dev \
    libzip-dev oniguruma-dev icu-dev libxml2-dev sqlite-dev

RUN docker-php-ext-configure gd --with-freetype --with-jpeg && \
    docker-php-ext-install -j$(nproc) \
    pdo_mysql pdo_sqlite mbstring exif pcntl bcmath gd zip intl opcache xml

RUN apk add --no-cache --virtual .build-deps $PHPIZE_DEPS && \
    pecl install redis && docker-php-ext-enable redis && \
    apk del .build-deps

WORKDIR /var/www/html

COPY --from=composer /app /var/www/html
COPY --from=node-builder /app/public/build /var/www/html/public/build
COPY docker/nginx.conf /etc/nginx/http.d/default.conf
COPY docker/supervisord.conf /etc/supervisord.conf
COPY docker/php.ini /usr/local/etc/php/conf.d/custom.ini

RUN mkdir -p storage/app/public storage/framework/{cache,sessions,views} storage/logs bootstrap/cache database && \
    rm -f public/storage && ln -s /var/www/html/storage/app/public public/storage && \
    chown -R www-data:www-data storage bootstrap/cache database && \
    chmod -R 775 storage bootstrap/cache database

EXPOSE 80
CMD ["/usr/bin/supervisord", "-c", "/etc/supervisord.conf"]
```

## 3. Docker Config Files

### docker/nginx.conf

```nginx
server {
    listen 80;
    server_name _;
    root /var/www/html/public;
    index index.php;

    client_max_body_size 100M;

    location / {
        try_files $uri $uri/ /index.php?$query_string;
    }

    location ~ \.php$ {
        fastcgi_pass 127.0.0.1:9000;
        fastcgi_index index.php;
        fastcgi_param SCRIPT_FILENAME $realpath_root$fastcgi_script_name;
        include fastcgi_params;
        fastcgi_buffering off;
        fastcgi_param HTTPS on;
    }

    location ~ /\.(?!well-known).* {
        deny all;
    }
}
```

### docker/php.ini

```ini
upload_max_filesize = 100M
post_max_size = 100M
memory_limit = 512M
max_execution_time = 120

[opcache]
opcache.enable=1
opcache.memory_consumption=128
opcache.max_accelerated_files=10000
opcache.validate_timestamps=0
```

### docker/supervisord.conf

```ini
[supervisord]
nodaemon=true
user=root
logfile=/var/log/supervisord.log

[program:php-fpm]
command=/usr/local/sbin/php-fpm -F
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0

[program:nginx]
command=/usr/sbin/nginx -g "daemon off;"
autostart=true
autorestart=true
stdout_logfile=/dev/stdout
stdout_logfile_maxbytes=0
stderr_logfile=/dev/stderr
stderr_logfile_maxbytes=0
```

## 4. docker-compose.traefik.yml

```yaml
services:
  app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: your-laravel-app
    restart: unless-stopped
    env_file:
      - .env
    mem_limit: 1g
    healthcheck:
      test: ["CMD", "wget", "-qO-", "http://127.0.0.1/up"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 30s
    volumes:
      - storage:/var/www/html/storage/app
      - database:/var/www/html/database
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.your-laravel.rule=Host(`app.yourdomain.com`)"
      - "traefik.http.routers.your-laravel.entrypoints=websecure"
      - "traefik.http.routers.your-laravel.tls=true"
      - "traefik.http.services.your-laravel.loadbalancer.server.port=80"
    networks:
      - web

  queue:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: your-laravel-queue
    restart: unless-stopped
    command: php artisan queue:work --sleep=3 --tries=3 --max-time=3600
    env_file:
      - .env
    volumes:
      - database:/var/www/html/database
    networks:
      - web
    depends_on:
      - app

volumes:
  storage:
  database:

networks:
  web:
    external: true
```

## 5. Deploy

```bash
# Build and start
docker compose -f docker-compose.traefik.yml build
docker compose -f docker-compose.traefik.yml up -d

# Run migrations
docker exec your-laravel-app php artisan migrate --force

# View logs
docker logs your-laravel-app -f
```

## Common Issues

### Vite Build Error: Ziggy not found
Copy vendor directory from composer stage to node stage in Dockerfile.

### HTTPS Redirect Loop
Add `fastcgi_param HTTPS on;` in nginx.conf.

### Health Check Fails with 302
Use `/up` endpoint instead of `/` for health checks.

## Next Steps

→ [Monitoring](06-monitoring.md)
