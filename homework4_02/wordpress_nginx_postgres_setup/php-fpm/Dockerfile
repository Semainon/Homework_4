Используем официальный образ PHP-FPM
FROM php:8.3-fpm

# Устанавливаем необходимые расширения для работы с PostgreSQL
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libzip-dev \
    unzip \
    libpq-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd pdo pdo_pgsql \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Создаем директорию для приложения, если она не существует, и устанавливаем права
RUN mkdir -p /var/www/html && chown -R www-data:www-data /var/www/html

# Создаем директорию для сокета, если она не существует, и устанавливаем права
RUN mkdir -p /var/run/php && \
    chown -R www-data:www-data /var/run/php && \
    chmod 770 /var/run/php

# Устанавливаем рабочую директорию
WORKDIR /var/www/html