### Д3 4.4. Контейниризовать простейший web-сервер на Python/Perl/Ruby/прочее 

### Общая структура файлов проекта
```bash
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
│   ├── Dockerfile
│   ├── requirements.txt
├   ├── models.py
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
### Добавляем в .env настройки и переменные для web-сервера на Python 
```bash
[root@Zero wordpress_nginx_postgres_setup]# nano .env 
[root@Zero wordpress_nginx_postgres_setup]# cat .env
# ===========================
# Настройки базы данных WordPress
# ===========================
DB_NAME=wordpress_db                 # Имя базы данных, используемой WordPress.
DB_USER=wordpress_user               # Имя пользователя для подключения к базе данных.
DB_PASSWORD=admin_password123        # Пароль для пользователя базы данных.

# ===========================
# Настройки администратора WordPress
# ===========================
WP_ADMIN_EMAIL=admin@example.com     # Электронная почта администратора WordPress.
WP_ADMIN_USER=admin                  # Имя администратора WordPress.
WP_ADMIN_PASSWORD=admin_password123  # Пароль администратора WordPress.

# ===========================
# Настройки домена и портов
# ===========================
DOMAIN_NAME=*****.ru                 # Имя домена.
HTTP_PORT=8080                       # Порт для WordPress.
PYTHON_SERVER_PORT=8000              # Порт для сервера на Python.

# ===========================
# Настройки базы данных для web-сервера на Python/Django 
# ===========================
PYTHON_DB_NAME=python_db             # Имя базы данных для web-сервера.
PYTHON_DB_USER=python_user           # Имя пользователя для подключения к базе данных web-сервера.
PYTHON_DB_PASSWORD=P@ssw0rd!2025     # Пароль для пользователя базы данных web-сервера.

# ===========================
# Учетные данные суперпользователя
# ===========================
SUPERUSER_USERNAME=admin              # Имя суперпользователя для web-сервера.
SUPERUSER_PASSWORD=SuperSecurePass!   # Пароль суперпользователя для web-сервера.

# ===========================
# Разрешенные хосты для web-сервера
# ===========================
ALLOWED_HOSTS=localhost,127.0.0.1,*****.ru, **.***.***.19

# ===========================
# Секретные ключи
# ===========================
SECRET_KEY=3x@mpl3S3cr3tK3y!2025        # Секретный ключ для web-сервера.
# ADDITIONAL_SECRET_KEY=An0therS3cr3tK3y! # Дополнительный секретный ключ.

# ===========================
# Режим отладки
# ===========================
DEBUG=True                             # Режим отладки.

# ===========================
# Переменная для IP адреса сервера
# ===========================
SERVER_IP=**.***.***.**                # IP адрес сервера.

# ===========================
# Grafana
# ===========================
# Пароль администратора Grafana в веб-интерфейсе, Логин: admin / Пароль: admin (по умолчанию)
GF_ADMIN_PASSWORD=admin_password123  # Устанавливаем свой пароль администратора Grafana

``` 
### Создаем веб-приложение на Python/Django, которое будет обслуживаться через Nginx и использовать SQLite в качестве базы данных:

```bash 
[root@Zero wordpress_nginx_postgres_setup]# cd python_server && ls
db.sqlite3  Dockerfile  manage.py  requirements.txt  zero
[root@Zero python_server]# cd zero && ls
create_superuser.py  __init__.py  __pycache__  settings.py  setup.py  templates  urls.py  views.py  wsgi.py

# Код в папке python_server: https://github.com/Semainon/Homework_4/tree/main/homework4_04/wordpress_nginx_postgres_setup/python_server 

# Структура проекта (Python/Django)   
python_server/
│
├── db.sqlite3               
├── Dockerfile                
├── manage.py                 
├── requirements.txt          
└── zero/                       # Основная директория приложения                
    ├── create_superuser.py   
    ├── __init__.py           
    ├── settings.py           
    ├── setup.py              
    ├── templates/            
    │   └── about.html        
    ├── urls.py               
    ├── views.py              
    └── wsgi.py              

``` 
### Обновляем docker-compose.yml    

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
    depends_on:
      - db
    networks:
      - wordpress_network
    ports:
      - "8080:80"
    # command: ["/usr/local/bin/install-wordpress.sh"]  # Запуск скрипта установки WordPres

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


  python_server:
    build:
      context: ./python_server  # Указываем путь к Dockerfile для Python-сервера
      dockerfile: Dockerfile
    container_name: python_server
    restart: always
    environment:
      PYTHON_DB_NAME: ${PYTHON_DB_NAME}  # Имя базы данных для Python-сервера
      PYTHON_DB_USER: ${PYTHON_DB_USER}  # Имя пользователя для подключения к базе данных Python-сервера
      PYTHON_DB_PASSWORD: ${PYTHON_DB_PASSWORD}  # Пароль для пользователя базы данных Python-сервера
      SUPERUSER_USERNAME: ${SUPERUSER_USERNAME}  # Имя суперпользователя
      SUPERUSER_PASSWORD: ${SUPERUSER_PASSWORD}  # Пароль суперпользователя
      ALLOWED_HOSTS: ${ALLOWED_HOSTS}  
      SECRET_KEY: ${SECRET_KEY}  # Секретный ключ
      DEBUG: ${DEBUG}  # Режим отладки
    volumes:
      - ./python_server:/app  # Копируем код приложения в контейнер
    ports:
      - "8000:8000"   
    networks:
      - wordpress_network
    command: python manage.py runserver 0.0.0.0:8000


  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      GF_DATABASE_TYPE: postgres
      GF_DATABASE_HOST: db:5432  # Указываем имя сервиса PostgreSQL
      GF_DATABASE_NAME: ${DB_NAME}  
      GF_DATABASE_USER: ${DB_USER}  
      GF_DATABASE_PASSWORD: ${DB_PASSWORD}  # Пароль пользователя PostgreSQL
      GF_SECURITY_ADMIN_PASSWORD: ${GF_ADMIN_PASSWORD}  # Устанавливаем пароль администратора (логин по умолчанию: admin)
    ports:
      - "3000:3000" 
    volumes:
      - grafana_data:/var/lib/grafana
    networks:
      - wordpress_network

volumes:
  wordpress_data:
  db_data:
  grafana_data: 
  #php-fpm-socket:  # Определение общего тома для сокета

networks:
  wordpress_network:
    driver: bridge  # Указываем драйвер сети

```
### Пересобираем проект  
```bash 
root@Zero wordpress_nginx_postgres_setup]# docker-compose down 
root@Zero wordpress_nginx_postgres_setup]# docker-compose build
root@Zero wordpress_nginx_postgres_setup]# docker-compose up -d  
...
root@Zero wordpress_nginx_postgres_setup]# docker-compose ps
NAME            IMAGE                                          COMMAND                  SERVICE         CREATED          STATUS         PORTS
db              postgres:latest                                "docker-entrypoint.s…"   db              10 seconds ago   Up 7 seconds   5432/tcp
grafana         grafana/grafana:latest                         "/run.sh"                grafana         10 seconds ago   Up 6 seconds   0.0.0.0:3000->3000/tcp
nginx           wordpress_nginx_postgres_setup-nginx           "/docker-entrypoint.…"   nginx           10 seconds ago   Up 7 seconds   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
php-fpm         wordpress_nginx_postgres_setup-php-fpm         "docker-php-entrypoi…"   php-fpm         10 seconds ago   Up 8 seconds   9000/tcp
python_server   wordpress_nginx_postgres_setup-python_server   "python manage.py ru…"   python_server   10 seconds ago   Up 8 seconds   0.0.0.0:8000->8000/tcp
wordpress       wordpress_nginx_postgres_setup-wordpress       "docker-entrypoint.s…"   wordpress       10 seconds ago   Up 6 seconds   0.0.0.0:8080->80/tcp
```