### Д3 4.2. Написать docker-compose.yaml, который:
- **Реализует сервис из задания выше**
- **Меняет пароль суперпользователя PostgreSQL**
- **Пароль и почту Wordpress**
Примечание:
- **Данные (пароли, почта) берутся из .env-файла**

### Общая структура файлов проекта, исходя из пунктов 1-6 ДЗ №4
```bash
# Предварительная структура файлов проекта
# Несколько Dockerfile дают возможность изолировать каждый сервис (для лучшей управляемости и масштабирумости)
wordpress_nginx_postgres_setup/
│
├── .env
├── docker-compose.yml
├── nginx/
│   ├── Dockerfile
│   ├── nginx.conf
│   └── html/
│       └── index.html  # Тестовая страница
├── wordpress/
│   ├── Dockerfile
│   └── create-wp-config.php  
├── python_server/
│   ├── app.py
│   └── Dockerfile
└── grafana/
    └── docker-compose.yml
```
### Создаем .env файл для хранения конфигурационных настроек и переменных окружения проекта	
```bash
[root@Zero wordpress_nginx_postgres_setup]# nano .env 
[root@Zero wordpress_nginx_postgres_setup]# cat .env
DB_NAME=wordpress_db                 # Имя базы данных, используемой WordPress.
DB_USER=wordpress_user               # Имя пользователя для подключения к базе данных.
DB_PASSWORD=secure_password123       # Пароль для пользователя базы данных.
WP_ADMIN_EMAIL=admin@example.com     # Электронная почта администратора WordPress.
WP_ADMIN_USER=admin                  # Имя администратора WordPress.
WP_ADMIN_PASSWORD=admin_password123  # Пароль администратора WordPress.
# DOMAIN_NAME=*****.ru                 # Имя домена.
HTTP_PORT=8080                       # Порт для wordpress.
PYTHON_SERVER_PORT=8000              # Порт для сервера на Python.
``` 
### Создаем docker-compose.yml  
- **docker-compose.yml — это конфигурационный файл, используемый инструментом Docker Compose для определения и управления многоконтейнерными приложениями. Этот файл позволяет разработчикам описывать, какие контейнеры должны быть запущены, как они должны взаимодействовать друг с другом, а также настраивать сети и тома для хранения данных.**
```bash 
[root@Zero wordpress_nginx_postgres_setup]# nano docker-compose.yml
root@Zero wordpress_nginx_postgres_setup]# cat docker-compose.yml
services:
  wordpress:
    image: wordpress:latest
    environment:
      WORDPRESS_DB_HOST: db
      WORDPRESS_DB_USER: ${DB_USER}
      WORDPRESS_DB_PASSWORD: ${DB_PASSWORD}
      WORDPRESS_DB_NAME: ${DB_NAME}
    ports:
      - "${HTTP_PORT}:80"  # Пробрасываем порт 8080 на 80 внутри контейнера
    volumes:
      - wordpress_data:/var/www/html
    networks:
      - wordpress_network

  nginx:
    build:
      context: ./nginx
      dockerfile: Dockerfile
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt  # Используем сертификаты из стандартной папки
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/html:/usr/share/nginx/html  
    networks:
      - wordpress_network

  db:
    image: postgres:latest
    environment:
      POSTGRES_DB: ${DB_NAME}
      POSTGRES_USER: ${DB_USER}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - db_data:/var/lib/postgresql/data
    networks:
      - wordpress_network

volumes:
  wordpress_data:
  db_data:

networks:
  wordpress_network:
```
### Обновляем nginx.conf
```bash 
worker_processes auto;

events {
    worker_connections 1024;
}

http {
    resolver 8.8.8.8;  # Google DNS

    # Настройки SSL
    ssl_protocols       TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers         'HIGH:!aNULL:!MD5';

    server {
        listen 80;
        server_name *****.ru www.*****.ru;

        # Редирект на HTTPS
        return 301 https://$host$request_uri;
    }

    server {
        listen 443 ssl http2;  # Включаем HTTP/2
        server_name *****.ru www.*****.ru;

        ssl_certificate /etc/letsencrypt/live/*****.ru/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/*****.ru/privkey.pem;

        location /.well-known/acme-challenge/ {
            root /usr/share/nginx/html;
        }

        location / {
            root /usr/share/nginx/html;  # Путь к директории с вашими файлами
            index index.html;
            try_files $uri $uri/ /index.html;  # Если файл не найден, отдаем index.html
        }

        location /wordpress {
            proxy_pass http://wordpress:80;  # Проксируем запросы к WordPress
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}
``` 
```bash 
[root@Zero wordpress_nginx_postgres_setup]# docker --version
Docker version 26.1.3, build b72abbb
[root@Zero wordpress_nginx_postgres_setup]# docker-compose --version
Docker Compose version v2.32.1
[root@Zero wordpress_nginx_postgres_setup]# docker-compose build  # Пересобираем после изменений
[root@Zero wordpress_nginx_postgres_setup]# docker-compose up -d  # Запускаем Docker Compose (флаг -d запускает контейнеры в фоновом режиме)
[root@Zero wordpress_nginx_postgres_setup]# docker-compose ps     # Проверяем статус контейнеров
[root@Zero wordpress_nginx_postgres_setup]# docker-compose run --rm certbot # Если еще нет сертификатов
# После внесения изменений в docker-compose.yml и конфигурацию Nginx, перезапускаем контейнеры:
[root@Zero wordpress_nginx_postgres_setup]# docker-compose down
[root@Zero wordpress_nginx_postgres_setup]# docker-compose up -d  
[root@Zero wordpress_nginx_postgres_setup]# docker-compose ps 
# смотрим логи, если есть проблемы с контейнером, в данном случае, с nginx   
[root@Zero wordpress_nginx_postgres_setup]# docker logs wordpress_nginx_postgres_setup-nginx-1  

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
