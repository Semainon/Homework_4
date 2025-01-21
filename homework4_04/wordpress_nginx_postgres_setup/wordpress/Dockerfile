# Используем официальный образ WordPress
FROM wordpress:latest

# Устанавливаем необходимые расширения для работы с PostgreSQL и устанавливаем WP-CLI
RUN apt-get update && apt-get install -y \
    libpng-dev \
    libjpeg-dev \
    libfreetype6-dev \
    libzip-dev \
    unzip \
    libpq-dev \
    && docker-php-ext-configure gd --with-freetype --with-jpeg \
    && docker-php-ext-install gd pdo pdo_pgsql \
    && curl -O https://raw.githubusercontent.com/wp-cli/builds/gh-pages/phar/wp-cli.phar \
    && chmod +x wp-cli.phar \
    && mv wp-cli.phar /usr/local/bin/wp \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Создаем директорию для приложения, если она не существует, и устанавливаем права
RUN mkdir -p /var/www/html && \
    chown -R www-data:www-data /var/www/html && \
    chmod -R 775 /var/www/html


# Установка прав доступа для wp-content
RUN chown -R www-data:www-data /var/www/html/wp-content

# Копируем скрипт в контейнер и устанавливаем права на выполнение
COPY install-wordpress.sh /usr/local/bin/install-wordpress.sh
RUN chmod +x /usr/local/bin/install-wordpress.sh

