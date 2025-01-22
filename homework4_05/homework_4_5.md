### Д3 4.5. Модернизировать конфигурацию:
- из первого задания таким образом, что бы логи и конфигурация nginx хранились не в docker-volume
- при обращении к http-path /myWebBack открывалась страница сервера из четвёртого задания 

### Справочная информация 
Типы томов:
- Named volumes: Это тома, которые создаются и управляются Docker. Они могут быть использованы несколькими контейнерами и хранятся в специальной области на хосте.
- Bind mounts: Это монтирование существующей директории на хосте в контейнер. Это позволяет контейнеру использовать файлы и директории, которые находятся на хосте.

По условию, логи и конфигурация nginx должны хранится в bind mounts, что обеспечивает прямой доступ к файлам на хосте.
 
### Общий формат:  
```bash
# Каждая строка в секции volumes имеет следующий формат:
<путь_на_хосте>:<путь_в_контейнере> 

# Пример: 
volumes: 
- ./nginx/nginx.conf:/etc/nginx/nginx.conf   


./nginx/nginx.conf: Путь к файлу конфигурации Nginx на хосте. 
/etc/nginx/nginx.conf: Путь, по которому Nginx в контейнере будет искать файл конфигурации. Т.о., при запуске контейнера Nginx будет использовать наш локальный файл конфигурации вместо стандартного.
```
### Структура файлов проекта
```bash
wordpress_nginx_postgres_setup/
├── .env
├── docker-compose.yml
├── init-superuser.sql
├── nginx/
│   ├── Dockerfile
│   ├── html/
│   ├── nginx.conf     # Конфигурация nginx 
│   └── logs/          # Папка для логов nginx
├── php-fpm/
│   ├── Dockerfile
│   ├── php-fpm.conf
│   └── www.conf
├── python_server/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── models.py
│   └── zero/
│       ├── __init__.py
│       ├── settings.py
│       ├── urls.py
│       ├── views.py         
│       ├── asgi.py
│       ├── wsgi.py
│       ├── setup.py
│       └── templates/      
│           └── about.html  
├── wordpress/
│   ├── Dockerfile
│   ├── install-wordpress.sh
│   └── wp-config.php
```

### Создаем папку logs и обновлем блок nginx в docker-compose.yml (для nginx.conf условие уже реализовано)
```bash
[root@Zero wordpress_nginx_postgres_setup]# mkdir -p ./nginx/logs
[root@Zero wordpress_nginx_postgres_setup]# nano docker-compose.yml 

# Редактируем блок nginx в docker-compose.yml 
  nginx:
    build:
      context: ./nginx  # Указываем путь к Dockerfile для Nginx
      dockerfile: Dockerfile
    container_name: nginx
    restart: always
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/logs:/var/log/nginx   # Монтируем директорию для логов
      - wordpress_data:/var/www/html
    depends_on:
      - php-fpm
    networks:
      - wordpress_network
    ports:
      - "80:80"
      - "443:443"
```

### Обновляем nginx.conf: указываем директории для логов и добавлеяем блок для обработки запросов к Django 
```bash
user www-data www-data;  # Указываем пользователя и группу для работы Nginx
worker_processes auto;   # Автоматически определяем количество рабочих процессов

events {
    worker_connections 1024;  # Максимальное количество соединений на один рабочий процесс
}

http {
    resolver 8.8.8.8;  # Google DNS

    # Настройки SSL
    ssl_protocols TLSv1.2 TLSv1.3;  # Поддерживаемые версии протоколов SSL
    ssl_prefer_server_ciphers on;    
    ssl_ciphers 'HIGH:!aNULL:!MD5'; 

    server {
        listen 80;  # Слушаем HTTP на порту 80
        server_name ****.ru www.****.ru;  # Заменено на звездочки

        # Редирект на HTTPS
        return 301 https://$host$request_uri;  # Перенаправляем на HTTPS
    }

    server {
        listen 443 ssl;  # Слушаем HTTPS на порту 443
        server_name ****.ru www.****.ru;  # Заменено на звездочки

        ssl_certificate /etc/letsencrypt/live/****.ru/fullchain.pem;  # Путь к SSL-сертификату
        ssl_certificate_key /etc/letsencrypt/live/****.ru/privkey.pem;  # Путь к закрытому ключу

        # Указываем директории для логов
        access_log /var/log/nginx/access.log;  # Лог доступа
        error_log /var/log/nginx/error.log;    # Лог ошибок

        location /.well-known/acme-challenge/ {
            root /usr/share/nginx/html;  # Путь для проверки сертификатов
        }

        # Основной блок для обработки запросов к WordPress
        location / {
            root /var/www/html;  # Путь к директории с файлами WordPress
            index index.php index.html;  # Указываем индексные файлы
            try_files $uri $uri/ /index.php?$args;  # Если файл не найден, отдаем index.php
        }

        # Обработка PHP-файлов через fastcgi_pass
        location ~ \.php$ {
            fastcgi_split_path_info ^(.+\.php)(/.+)$;  # Разделяем SCRIPT_NAME и PATH_INFO
            include fastcgi_params;  # Включаем стандартные параметры FastCGI
            fastcgi_pass php-fpm:9000;  # Проксируем запросы на PHP-FPM по IP и порту
            fastcgi_index index.php;  # Указываем индексный файл
            fastcgi_param SCRIPT_FILENAME $document_root$fastcgi_script_name;  # Указываем путь к скрипту
            fastcgi_param PATH_INFO $fastcgi_path_info;  # Передаем PATH_INFO
        }

        # Основной блок для обработки запросов к Django
        location /myWebBack/ {  
            proxy_pass http://python_server:8000;  # Проксируем запросы на Django
            proxy_set_header Host $host;  # Передаем заголовок Host
            proxy_set_header X-Real-IP $remote_addr;  # Передаем IP клиента
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;  # Передаем информацию о прокси
            proxy_set_header X-Forwarded-Proto $scheme;  # Передаем протокол
        }
    }
}
```

```bash
[root@Zero nginx]# docker exec nginx nginx -t
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful 
```
