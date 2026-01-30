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
# Copy vendor for packages like Ziggy that need PHP dependencies
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
