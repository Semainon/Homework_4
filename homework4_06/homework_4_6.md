### Д3 4.6. Написать CI/CD-pipeline, который:
- использует переменные (имена пользователей СУБД, пароли, номера портов и тд)
- тестирует сборку контейнера и его работу ( доступность Grafana, работу Wordpress и сервера из 4 задания)
- доставляет собранный контейнер на конечную машину
- запускает контейнер на удалённой машине
 
### Итоговая структура файлов проекта
```bash
wordpress_nginx_postgres_setup/
├── .env
├── docker-compose.yml
├── init-superuser.sql
├── nginx/
│   ├── Dockerfile
│   ├── html/
│   ├── logs/
│   └── nginx.conf
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
└── .github/
    └── workflows/
        └── ci-cd-pipeline.yml
```
### Создаем шаблон env.example 
```bash 

# =======================================
# Шаблон файла .env 
# =======================================
# 1. Скопируйте этот шаблон в файл .env на вашем сервере.
# 2. Замените все значения по умолчанию на реальные данные, соответствующие вашей среде.
# 3. Убедитесь, что файл .env не отслеживается системой контроля версий (добавьте его в .gitignore).
# 4. Перезапустите ваше приложение, чтобы изменения вступили в силу.

# =======================================
# Шаблон файла .env для настройки приложения
# =======================================

# Настройки базы данных WordPress
DB_NAME=wordpress_db                 # Имя базы данных, используемой WordPress.
DB_USER=wordpress_user               # Имя пользователя для подключения к базе данных.
DB_PASSWORD=admin_password123        # Пароль для пользователя базы данных.

# Настройки администратора WordPress
WP_ADMIN_EMAIL=admin@example.com     # Электронная почта администратора WordPress.
WP_ADMIN_USER=admin                  # Имя администратора WordPress.
WP_ADMIN_PASSWORD=admin_password123  # Пароль администратора WordPress.

# Переменная для IP адреса сервера, домена и портов
SERVER_IP=**.***.***.**                # IP адрес сервера.
DOMAIN_NAME=*****.ru                 # Имя домена.
HTTP_PORT=8080                       # Порт для WordPress.
PYTHON_SERVER_PORT=8000              # Порт для сервера на Python.

# Grafana
GF_ADMIN_PASSWORD=admin_password123  # Устанавливаем свой пароль администратора Grafana.

# =======================================
# Настройки для проекта на Python/Django 
# =======================================

# Настройки базы данных 
PYTHON_DB_NAME=python_db             # Имя базы данных для web-сервера.
PYTHON_DB_USER=python_user           # Имя пользователя для подключения к базе данных web-сервера.
PYTHON_DB_PASSWORD=P@ssw0rd!2025     # Пароль для пользователя базы данных web-сервера.

# Учетные данные суперпользователя 
SUPERUSER_USERNAME=admin              # Имя суперпользователя для web-сервера.
SUPERUSER_PASSWORD=SuperSecurePass!   # Пароль суперпользователя для web-сервера.

# Разрешенные хосты 
ALLOWED_HOSTS=localhost,127.0.0.1,*****.ru, **.***.***.19

# Секретные ключи 
SECRET_KEY=3x@mpl3S3cr3tK3y!2025        # Секретный ключ для web-сервера.
# ADDITIONAL_SECRET_KEY=An0therS3cr3tK3y! # Дополнительный секретный ключ.

# Режим отладки
DEBUG=True                             

```
### Шаги по настройке и тестированию

- Создаем файл .env на сервер с необходимыми переменными окружения для проекта.
- Убедимся, что на удаленном сервере установлен Docker и Docker Compose. 
- Добавляем секреты в GitHub: Переходим в настройки репозитория на GitHub и добавляем необходимые секреты.
- Тестирование: Делаем пуш в ветку main или создаем пулл-реквест, чтобы запустить CI/CD Pipeline. Проверяем логи выполнения на GitHub Actions, чтобы убедиться, что все шаги прошли успешно.
- После успешного выполнения пайплайна проверяем, что контейнеры запущены на удаленном сервере и доступны по указанным портам.

### Добавление секретов в репозитории на GitHub:

Перейти в репозиторий → "Settings" (Настройки) →  "Secrets and variables" (Секреты и переменные) →  "Actions" (Действия) →  "New repository secret" (Добавиляем новый секрет) → "Name" (Имя секрета, например, DB_PASSWORD ) → "Value" (Значение, например,dmin_password123) → "Add secret" → Повторяем для всех секретов.

```bash 
DB_NAME: Имя базы данных для WordPress.
DB_USER: Имя пользователя для подключения к базе данных.
DB_PASSWORD: Пароль для пользователя базы данных.
WP_ADMIN_EMAIL: Электронная почта администратора WordPress.
WP_ADMIN_USER: Имя администратора WordPress.
WP_ADMIN_PASSWORD: Пароль администратора WordPress.
DOMAIN_NAME: Имя домена.
HTTP_PORT: Порт для WordPress.
PYTHON_SERVER_PORT: Порт для сервера на Python.
PYTHON_DB_NAME: Имя базы данных для web-сервера на Python.
PYTHON_DB_USER: Имя пользователя для подключения к базе данных web-сервера.
PYTHON_DB_PASSWORD: Пароль для пользователя базы данных web-сервера.
SUPERUSER_USERNAME: Имя суперпользователя для web-сервера.
SUPERUSER_PASSWORD: Пароль суперпользователя для web-сервера.
ALLOWED_HOSTS: Разрешенные хосты для web-сервера.
SECRET_KEY: Секретный ключ для web-сервера.
DEBUG: Режим отладки (например, True или False).
SERVER_IP: IP адрес сервера.
GF_ADMIN_PASSWORD: Пароль администратора Grafana.
SSH_PRIVATE_KEY: Приватный SSH-ключ для доступа к удаленному серверу.
REMOTE_USER: Имя пользователя для SSH-доступа к удаленному серверу.
REMOTE_HOST: IP-адрес или доменное имя удаленного сервера.

```
###  Создание файла конфигурации GitHub Actions 
События: Пайплайн запускается при пуше в ветку main и при создании пулл-реквеста в эту ветку.
Шаги:
- Checkout code: Загружает код нашего репозитория.
- Load environment variables: Загружает переменные окружения из секретов GitHub в окружение, чтобы они могли быть использованы в последующих шагах.
- Set up Docker Buildx: Настраивает Docker Buildx для сборки образов.
- Build Docker images: Сборка образов для каждого сервиса (WordPress, PHP-FPM, Nginx, Python Server).
- Pull Grafana and PostgreSQL Docker images: Загружает официальные образы Grafana и PostgreSQL.
- Test Docker containers: Запускает временные контейнеры для тестирования доступности WordPress и Grafana.
- Deploy to remote server: Копирует файл docker-compose.yml на удаленный сервер и запускает контейнеры.


```bash
# Создаем директорию .github/workflows в корне проекта
[root@Zero wordpress_nginx_postgres_setup]# mkdir .github
[root@Zero wordpress_nginx_postgres_setup]# mkdir .github/workflows
[root@Zero workflows]# nano ci-cd-pipeline.yml 

# Код пайплайна

name: CI/CD Pipeline  # Название пайплайна

on:
  push:
    branches:
      - main  # Запускать пайплайн при пуше в ветку main
  pull_request:
    branches:
      - main  # Запускать пайплайн при создании пулл-реквеста в ветку main

jobs:
  build:  # Определение работы с именем 'build'
    runs-on: ubuntu-latest  # Указать, что работа будет выполняться на последней версии Ubuntu

    steps:  # Шаги, которые будут выполнены в рамках работы
      - name: Checkout code  # Шаг для извлечения кода из репозитория
        uses: actions/checkout@v2  # Использовать действие для извлечения кода

      - name: Load environment variables  # Шаг для загрузки переменных окружения
        run: |  # Загрузка переменных из секретов
          echo "DB_NAME=${{ secrets.DB_NAME }}" >> $GITHUB_ENV  
          echo "DB_USER=${{ secrets.DB_USER }}" >> $GITHUB_ENV  
          echo "DB_PASSWORD=${{ secrets.DB_PASSWORD }}" >> $GITHUB_ENV  
          echo "WP_ADMIN_EMAIL=${{ secrets.WP_ADMIN_EMAIL }}" >> $GITHUB_ENV  
          echo "WP_ADMIN_USER=${{ secrets.WP_ADMIN_USER }}" >> $GITHUB_ENV  
          echo "WP_ADMIN_PASSWORD=${{ secrets.WP_ADMIN_PASSWORD }}" >> $GITHUB_ENV  
          echo "DOMAIN_NAME=${{ secrets.DOMAIN_NAME }}" >> $GITHUB_ENV  
          echo "HTTP_PORT=${{ secrets.HTTP_PORT }}" >> $GITHUB_ENV  
          echo "PYTHON_SERVER_PORT=${{ secrets.PYTHON_SERVER_PORT }}" >> $GITHUB_ENV   
          echo "PYTHON_DB_NAME=${{ secrets.PYTHON_DB_NAME }}" >> $GITHUB_ENV  
          echo "PYTHON_DB_USER=${{ secrets.PYTHON_DB_USER }}" >> $GITHUB_ENV  
          echo "PYTHON_DB_PASSWORD=${{ secrets.PYTHON_DB_PASSWORD }}" >> $GITHUB_ENV  
          echo "SUPERUSER_USERNAME=${{ secrets.SUPERUSER_USERNAME }}" >> $GITHUB_ENV   
          echo "SUPERUSER_PASSWORD=${{ secrets.SUPERUSER_PASSWORD }}" >> $GITHUB_ENV  
          echo "ALLOWED_HOSTS=${{ secrets.ALLOWED_HOSTS }}" >> $GITHUB_ENV  
          echo "SECRET_KEY=${{ secrets.SECRET_KEY }}" >> $GITHUB_ENV  
          echo "DEBUG=${{ secrets.DEBUG }}" >> $GITHUB_ENV  
          echo "SERVER_IP=${{ secrets.SERVER_IP }}" >> $GITHUB_ENV  
          echo "GF_ADMIN_PASSWORD=${{ secrets.GF_ADMIN_PASSWORD }}" >> $GITHUB_ENV  

      - name: Set up Docker Buildx  # Шаг для настройки Docker Buildx
        uses: docker/setup-buildx-action@v1  # Использовать действие для настройки Buildx

      - name: Build Docker images  # Шаг для сборки Docker-образов
        run: |  
          docker build -t wordpress_nginx_postgres_setup-wordpress:latest ./wordpress  # Сборка образа WordPress
          docker build -t wordpress_nginx_postgres_setup-php-fpm:latest ./php-fpm  # Сборка образа PHP-FPM
          docker build -t wordpress_nginx_postgres_setup-nginx:latest ./nginx  # Сборка образа Nginx
          docker build -t wordpress_nginx_postgres_setup-python_server:latest ./python_server  # Сборка образа Python-сервера

      - name: Pull Grafana Docker image  # Шаг для загрузки образа Grafana
        run: |
          docker pull grafana/grafana:latest  # Загрузка последней версии образа Grafana

      - name: Pull PostgreSQL Docker image  # Шаг для загрузки образа PostgreSQL
        run: |
          docker pull postgres:latest  # Загрузка последней версии образа PostgreSQL

      - name: Test Docker containers  # Шаг для тестирования Docker-контейнеров
        run: |  # Выполнение нескольких команд
          docker run -d --name test_wordpress -p ${{ env.HTTP_PORT }}:80 wordpress_nginx_postgres_setup-wordpress:latest  # Запуск контейнера WordPress
          sleep 30  # Ожидание 30 секунд для инициализации
          curl -f http://localhost:${{ env.HTTP_PORT }} || exit 1  # Проверка доступности WordPress
          docker stop test_wordpress  # Остановка контейнера WordPress
          docker rm test_wordpress  # Удаление контейнера WordPress

          docker run -d --name test_grafana -p 3000:3000 grafana/grafana:latest  # Запуск контейнера Grafana
          sleep 30  # Ожидание 30 секунд для инициализации
          curl -f http://localhost:3000 || exit 1  # Проверка доступности Grafana
          docker stop test_grafana  # Остановка контейнера Grafana
          docker rm test_grafana  # Удаление контейнера Grafana

      - name: Deploy to remote server  # Шаг для развертывания на удаленном сервере
        env:  # Определение переменных окружения для этого шага
          SSH_PRIVATE_KEY: ${{ secrets.SSH_PRIVATE_KEY }}  # Загрузка приватного ключа SSH из секретов
          REMOTE_USER: ${{ secrets.REMOTE_USER }}  # Загрузка имени пользователя удаленного сервера из секретов
          REMOTE_HOST: ${{ secrets.REMOTE_HOST }}  # Загрузка адреса удаленного сервера из секретов
        run: |  
          echo "$SSH_PRIVATE_KEY" > private_key  # Сохранение приватного ключа в файл
          chmod 600 private_key  # Установка прав доступа к файлу ключа
          #  Заменить /path/to/deploy/ на полный путь к директории, где будет храниться docker-compose.yml:
          scp -i private_key -o StrictHostKeyChecking=no docker-compose.yml $REMOTE_USER@$REMOTE_HOST:/path/to/deploy/  # Копирование файла docker-compose.yml на удаленный сервер
          ssh -i private_key -o StrictHostKeyChecking=no $REMOTE_USER@$REMOTE_HOST "cd /path/to/deploy && docker-compose pull && docker-compose up -d"  # Подключение к удаленному серверу и запуск контейнеров с помощью docker-compose
```

