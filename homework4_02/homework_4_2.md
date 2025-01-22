### Д3 4.2. Написать docker-compose.yaml, который:
- **Реализует сервис из задания выше**
- **Меняет пароль суперпользователя PostgreSQL**
- **Пароль и почту Wordpress**
Примечание:
- **Данные (пароли, почта) берутся из .env-файла**

### Cруктура файлов проекта
```bash
# Предварительная структура файлов проекта
# Несколько Dockerfile дают возможность изолировать каждый сервис (для лучшей управляемости и масштабирумости)

wordpress_nginx_postgres_setup/
├── .env
├── docker-compose.yml
├── init-superuser.sql
├── nginx/
│   ├── Dockerfile
│   ├── html/
│   └── nginx.conf
├── php-fpm/
│   ├── Dockerfile
│   ├── php-fpm.conf
│   └── www.conf
├── python_server/
│   ├── app.py
│   └── Dockerfile
├── wordpress/
│   ├── Dockerfile
│   ├── install-wordpress.sh
│   └── wp-config.php
└── grafana

```
### Создаем .env файл для хранения конфигурационных настроек и переменных окружения проекта	
```bash
[root@Zero wordpress_nginx_postgres_setup]# nano .env 
[root@Zero wordpress_nginx_postgres_setup]# cat .env
D
DB_NAME=wordpress_db                  # Имя базы данных, используемой WordPress.
DB_USER=wordpress_user                # Имя пользователя для подключения к базе данных.
DB_PASSWORD=secure_password123        # Пароль для пользователя базы данных.
WP_ADMIN_EMAIL=admin@example.com      # Электронная почта администратора WordPress.
WP_ADMIN_USER=admin                   # Имя администратора WordPress.
WP_ADMIN_PASSWORD=admin_password123   # Пароль администратора WordPress.
SUPERUSER_NAME=superuser              # Имя суперпользователя PostgreSQL.
SUPERUSER_PASSWORD=superuser_password # Пароль суперпользователя PostgreSQL.
DOMAIN_NAME=*****.ru                  # Имя домена.
HTTP_PORT=8080                        # Порт для wordpress.
PYTHON_SERVER_PORT=8000               # Порт для сервера на Python.
``` 
### Создаем docker-compose.yml  
- **docker-compose.yml — это конфигурационный файл, используемый инструментом Docker Compose для определения и управления многоконтейнерными приложениями. Этот файл позволяет разработчикам описывать, какие контейнеры должны быть запущены, как они должны взаимодействовать друг с другом, а также настраивать сети и тома для хранения данных.**
```bash 
[root@Zero wordpress_nginx_postgres_setup]# nano docker-compose.yml
root@Zero wordpress_nginx_postgres_setup]# cat docker-compose.yml

services:
  wordpress:
    build:
      context: ./wordpress   # Указываем путь к Dockerfile для WordPress
      dockerfile: Dockerfile
    container_name: wordpress
    restart: always
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: ${DB_USER}
      WORDPRESS_DB_PASSWORD: ${DB_PASSWORD}
      WORDPRESS_DB_NAME: ${DB_NAME}
      DOMAIN_NAME: ${DOMAIN_NAME}  # Добавляем переменную для домена
      WP_ADMIN_USER: ${WP_ADMIN_USER}  # Имя администратора
      WP_ADMIN_PASSWORD: ${WP_ADMIN_PASSWORD}  # Пароль администратора
      WP_ADMIN_EMAIL: ${WP_ADMIN_EMAIL}  # Email администратора
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - wordpress_network
    command: ["/usr/local/bin/install-wordpress.sh"]  # Запуск скрипта установки WordPres

  php-fpm:
    build:
      context: ./php-fpm  # Указываем путь к Dockerfile для PHP-FPM
      dockerfile: Dockerfile
    container_name: php-fpm
    restart: always
    volumes:
      - wordpress_data:/var/www/html
      - ./wordpress/install-wordpress.sh:/usr/local/bin/install-wordpress.shl
      #- php-fpm-socket:/var/run/php  # Общий том для сокета
      - ./php-fpm/www.conf:/usr/local/etc/php-fpm.d/www.conf
      - ./php-fpm/php-fpm.conf:/usr/local/etc/php-fpm.conf
    networks:
      - wordpress_network
    #environment:
     # - PHP_FPM_LISTEN=/var/run/php/php-fpm.sock  # Указываем путь к сокету

  nginx:
    build:
      context: ./nginx  # Указываем путь к Dockerfile для Nginx
      dockerfile: Dockerfile
    container_name: nginx
    restart: always
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - wordpress_data:/var/www/html
      #- php-fpm-socket:/var/run/php  # Общий том для сокета
    depends_on:
      - php-fpm
    networks:
      - wordpress_network
    ports:
      - "80:80"
      - "443:443"

  db:
    image: postgres:latest
    container_name: db
    restart: always
    environment:
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_DB: ${DB_NAME}
    volumes:
      - db_data:/var/lib/postgresql/data
      - ./init-superuser.sql:/docker-entrypoint-initdb.d/init-superuser.sql  # Добавляем скрипт инициализации
    networks:
      - wordpress_network

volumes:
  wordpress_data:
  db_data:
  #php-fpm-socket:  # Определение общего тома для сокета

networks:
  wordpress_network:
    driver: bridge  # Указываем драйвер сети
```
### Создаем необхлодимые директории и файлы 

### WordPress  
```bash 
[root@Zero wordpress]# ls 
Dockerfile  install-wordpress.sh  wp-config.php


[root@Zero wordpress]# cat install-wordpress.sh
#!/bin/bash

# Ждем, пока база данных станет доступной
until pg_isready -h db -U ${DB_USER}; do
  echo "Waiting for PostgreSQL..."
  sleep 2
done

# Установка WordPress
wp core install --url="${DOMAIN_NAME}" --title="My WordPress Site" --admin_user="${WP_ADMIN_USER}" --admin_password="${WP_ADMIN_PASSWORD}" --admin_email="${WP_ADMIN_EMAIL}" --path="/var/www/html"

[root@Zero wordpress_nginx_postgres_setup]# cat wordpress/Dockerfile 

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
    postgresql-client \  
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

[root@Zero wordpress]# cat  wp-config.php
# define('DB_NAME', 'wordpress_db');               // Имя базы данных, используемой WordPress.
# define('DB_USER', 'wordpress_user');             // Имя пользователя для подключения к базе данных.
# define('DB_PASSWORD', 'secure_password123');     // Пароль для пользователя базы данных.
# define('DB_HOST', 'localhost');                   // Если база данных находится на том же сервере

# // Включение режима отладки
# define('WP_DEBUG', true);                         // Включает режим отладки
# define('WP_DEBUG_LOG', true);                     // Записывает ошибки в файл debug.log в wp-content
# define('WP_DEBUG_DISPLAY', true);                 // Отображает ошибки на экране
# @ini_set('display_errors', 1);                   // Включает отображение ошибок PHPr

define('DB_NAME', getenv('DB_NAME'));               // Имя базы данных, используемой WordPress.
define('DB_USER', getenv('DB_USER'));               // Имя пользователя для подключения к базе данных.
define('DB_PASSWORD', getenv('DB_PASSWORD'));       // Пароль для пользователя базы данных.
define('DB_HOST', getenv('DB_HOST') ?: 'localhost'); // Если база данных находится на том же сервере

// Включение режима отладки
define('WP_DEBUG', true);                           // Включает режим отладки
define('WP_DEBUG_LOG', true);                       // Записывает ошибки в файл debug.log в wp-content
define('WP_DEBUG_DISPLAY', true);                   // Отображает ошибки на экране
@ini_set('display_errors', 1);                     // Включает отображение ошибок PHP

```

### Nginx
```bash
[root@Zero wordpress_nginx_postgres_setup]# ls nginx/
Dockerfile  html  nginx.conf
[root@Zero wordpress_nginx_postgres_setup]# cat nginx/nginx.conf 

user www-data www-data;  # Указываем пользователя и группу для работы Nginx
worker_processes auto;   # Автоматически определяем количество рабочих процессов

events {
    worker_connections 1024;  # Максимальное количество соединений на один рабочий процесс
}

http {
    resolver 8.8.8.8;  # Google DNS

    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;  # Поддерживаемые версии протоколов SSL
    ssl_prefer_server_ciphers on;    # Предпочтение шифров сервера
    ssl_ciphers 'HIGH:!aNULL:!MD5';  # Поддерживаемые шифры

    server {
        listen 80;  # Слушаем HTTP на порту 80
        server_name ******.ru www.******.ru;  # Указываем доменные имена

        # Редирект на HTTPS
        return 301 https://$host$request_uri;  # Перенаправляем на HTTPS
    }

    server {
        listen 443 ssl;  # Слушаем HTTPS на порту 443
        server_name ******.ru www.a******.ru;  # Указываем доменные имена

        ssl_certificate /etc/letsencrypt/live/******.ru/fullchain.pem;  # Путь к SSL-сертификату
        ssl_certificate_key /etc/letsencrypt/live/******.ru/privkey.pem;  # Путь к закрытому ключу

        # Для проверки сертификатов Lets Encrypt
        location /.well-known/acme-challenge/ {
            root /usr/share/nginx/html;  # Путь для проверки сертификатов
        }

        # Основной блок для обработки запросов
        location / {
            root /var/www/html;  # Путь к директории с файлами
            index index.php index.html;  # Указываем индексные файлы
            try_files $uri $uri/ /index.php?$args;  # Если файл не найден, отдаем index.php
        }

        # Обработка PHP-файлов через fastcgi_pass
        location ~ \.php$ {
            fastcgi_split_path_info ^(.+\.php)(/.+)$;  # Разделяем SCRIPT_NAME и PATH_INFO
            include fastcgi_params;  # Включаем стандартные параметры FastCGI
            #fastcgi_pass unix:/var/run/php/php-fpm.sock;  # Проксируем запросы на PHP-FPM через сокет
            # fastcgi_pass 127.0.0.1:9000; 
            fastcgi_pass php-fpm:9000;  # Если  Проксируем запросы на PHP-FPM по IP и порту1
            fastcgi_index index.php;  # Указываем индексный файл
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;  # Указываем путь к скрипту
            fastcgi_param PATH_INFO $fastcgi_path_info;  # Передаем PATH_INFO
        }
    }
}

[root@Zero wordpress_nginx_postgres_setup]# cat nginx/Dockerfile 
# Используем официальный образ Nginx
FROM nginx:latest

# Создаем необходимые директории, если они не существуют
RUN mkdir -p /usr/share/nginx/html/.well-known/acme-challenge

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Копируем статические файлы (если есть)
COPY ./html /usr/share/nginx/html

# Открытие порта 80 для HTTP и 443 для HTTPS
EXPOSE 80
EXPOSE 443

# Запуск Nginx
CMD ["nginx", "-g", "daemon off;"]
```
### PHP-FPM 
```bash
[root@Zero wordpress_nginx_postgres_setup]# ls  php-fpm 
Dockerfile  php-fpm.conf  www.conf 
[root@Zero php-fpm]# cat Dockerfile
# Используем официальный образ PHP-FPM
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

[root@Zero php-fpm]# cat php-fpm.conf
[global]
error_log = /var/log/php-fpm.log
log_level = notice

include=/usr/local/etc/php-fpm.d/*.conf

[root@Zero php-fpm]# cat www.conf 
[www]
listen = 127.0.0.1:9000  
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
user = www-data
group = www-data
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
request_terminate_timeout = 30s
catch_workers_output = yes
php_flag[display_errors] = on
php_value[error_log] = /var/log/php-fpm/www-error.log
php_value[session.save_path] = /var/lib/php/sessions
php_admin_value[error_log] = /var/log/php-fpm/www-error.log
php_admin_flag[log_errors] = on
```

### Опционально: (Certbot / выпуск бесплатных SSL-сертификатов для настройки доступа по HTTPS) 
```bash
# для Oracle Linux 8
sudo dnf update -y
sudo dnf install epel-release -y 
sudo dnf install certbot python3-certbot-nginx -y 
# Certbot автоматически создает необходимые директории, но можно создать вручную:
sudo mkdir -p /etc/letsencrypt/live
sudo mkdir -p /etc/letsencrypt/archive
sudo mkdir -p /etc/letsencrypt/renewal
# Команда для выпуска сертификатов без настройки nginx (порт 80 должен быть не занят)
sudo certbot certonly --standalone
# Certbot автоматически устанавливает cron-задачу для обновления сертификатов. 
sudo systemctl status certbot.timer 
# Создаем вручную, если автоматически таймер не добавился
sudo nano /etc/systemd/system/certbot.timer
sudo nano /etc/systemd/system/certbot.service 
``` 
### Содержимое файла certbot.timer 
```bash 
[Unit]
Description=Run certbot twice daily

[Timer]
OnCalendar=*-*-* *:*:00
Persistent=true

[Install]
WantedBy=timers.target

```
### Содержимое файла certbot.service 
```bash 
[Unit]
Description=Certbot
Documentation=https://certbot.eff.org/docs/
After=network.target

[Service]
Type=oneshot
ExecStart=/usr/bin/certbot renew --quiet

[Install]
WantedBy=multi-user.target
``` 
### Активируем таймер и проверяем статус 
```bash  
sudo systemctl daemon-reload
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer
sudo systemctl status certbot.timer

```
### Создаем тестоввые файлы с разными расширениями и копируем в контейнер 
```bash  
[root@Zero wordpress_nginx_postgres_setup]# echo -e "User-agent: *\nDisallow: /wp-admin/\nDisallow: /wp-includes/\nAllow: /wp-admin/admin-ajax.php\n\nSitemap: https://******.ru/sitemap.xml" > robots.txt
[root@Zero wordpress_nginx_postgres_setup]# echo "<?php phpinfo(); ?>" > test.php
[root@Zero wordpress_nginx_postgres_setup]# cp ./services.html wordpress_nginx_postgres_setup-nginx-1:/var/www/html/test.php
[root@Zero wordpress_nginx_postgres_setup]# docker cp ./robots.txt wordpress_nginx_postgres_setup-nginx-1:/var/www/html/robots.txt 
[root@Zero wordpress_nginx_postgres_setup]# nano services.html
[root@Zero wordpress_nginx_postgres_setup]# cp ./services.html wordpress_nginx_postgres_setup-nginx-1:/var/www/html/test.php
```

### Конфиг для мспользования сокета для PHP-FPM в Nginx 
```bash  
docker exec -it wordpress_nginx_postgres_setup-php-fpm-1 /bin/bash # подлючаемся к терминалу контейнера php-fpm
cd /usr/local/etc/php-fpm.d/
# cоздаем  файл www.conf  
# если хотим использовать IP-адрес и порт в listen указываем listen = 0.0.0.0:9000 
cat <<EOL > www.conf 
[www]
listen = /var/run/php/php8.3-fpm.sock  
listen.owner = www-data
listen.group = www-data
listen.mode = 0660
user = www-data
group = www-data
pm = dynamic
pm.max_children = 5
pm.start_servers = 2
pm.min_spare_servers = 1
pm.max_spare_servers = 3
request_terminate_timeout = 30s
catch_workers_output = yes
php_flag[display_errors] = on
php_value[error_log] = /var/log/php-fpm/www-error.log
php_value[session.save_path] = /var/lib/php/sessions
php_admin_value[error_log] = /var/log/php-fpm/www-error.log
php_admin_flag[log_errors] = on
EOL
```
