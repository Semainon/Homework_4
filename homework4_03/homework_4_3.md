### Д3 4.3 Написать docker-compose.yaml, который реализует Grafana. Данные в TSDB этой Grafana-ы наполняются из значений метрик PostgreSQL из задания выше.

### Общая структура проекта, исходя из пунктов 1-6 ДЗ №4
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
│   ├── app.py
│   └── Dockerfile
├── wordpress/
│   ├── Dockerfile
│   ├── install-wordpress.sh
│   └── wp-config.php


```
### .env файл для хранения конфигурационных настроек и переменных окружения проекта	
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

  grafana:
    image: grafana/grafana:latest
    container_name: grafana
    restart: unless-stopped
    environment:
      GF_DATABASE_TYPE: postgres
      GF_DATABASE_HOST: db:5432  # Указываем имя сервиса PostgreSQL
      GF_DATABASE_NAME: ${DB_NAME}  # Имя базы данных WordPress
      GF_DATABASE_USER: ${DB_USER}  # Имя пользователя PostgreSQL
      GF_DATABASE_PASSWORD: ${DB_PASSWORD}  # Пароль пользователя PostgreSQL
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
root@Zero wordpress_nginx_postgres_setup]# docker-compose up -d
[+] Running 11/11
 ✔ grafana Pulled                                                                                                                                               36.0s 
   ✔ da9db072f522 Pull complete                                                                                                                                  2.6s 
   ✔ ebcbc122b722 Pull complete                                                                                                                                  2.8s 
   ✔ b2ddcf85da57 Pull complete                                                                                                                                  3.8s 
   ✔ 00a90dd48f56 Pull complete                                                                                                                                  4.0s 
   ✔ d7013a437817 Pull complete                                                                                                                                  4.0s 
   ✔ 1739eaecb10c Pull complete                                                                                                                                  4.0s 
   ✔ 8964b0551c55 Pull complete                                                                                                                                 29.6s 
   ✔ e0862465767a Pull complete                                                                                                                                 33.8s 
   ✔ 989e41ffb5ca Pull complete                                                                                                                                 33.8s 
   ✔ 9b4925e32b92 Pull complete                                                                                                                                 33.8s 
[+] Running 7/7
 ✔ Network wordpress_nginx_postgres_setup_wordpress_network  Created                                                                                             0.1s 
 ✔ Volume "wordpress_nginx_postgres_setup_grafana_data"      Created                                                                                             0.0s 
 ✔ Container php-fpm                                         Started                                                                                             1.1s 
 ✔ Container db                                              Started                                                                                             1.0s 
 ✔ Container grafana                                         Started                                                                                             1.2s 
 ✔ Container nginx                                           Started                                                                                             2.2s 
 ✔ Container wordpress                                       Started                                                                                             1.9s 
[root@Zero wordpress_nginx_postgres_setup]# docker-compose ps
NAME        IMAGE                                      COMMAND                  SERVICE     CREATED         STATUS         PORTS
db          postgres:latest                            "docker-entrypoint.s…"   db          7 seconds ago   Up 6 seconds   5432/tcp
grafana     grafana/grafana:latest                     "/run.sh"                grafana     7 seconds ago   Up 4 seconds   0.0.0.0:3000->3000/tcp
nginx       wordpress_nginx_postgres_setup-nginx       "/docker-entrypoint.…"   nginx       7 seconds ago   Up 5 seconds   0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
php-fpm     wordpress_nginx_postgres_setup-php-fpm     "docker-php-entrypoi…"   php-fpm     7 seconds ago   Up 6 seconds   9000/tcp
wordpress   wordpress_nginx_postgres_setup-wordpress   "docker-entrypoint.s…"   wordpress   7 seconds ago   Up 5 seconds   80/tcp
[root@Zero wordpress_nginx_postgres_setup]# cat .env
DB_NAME=wordpress_db                 # Имя базы данных, используемой WordPress.
DB_USER=wordpress_user               # Имя пользователя для подключения к базе данных.
DB_PASSWORD=secure_password123       # Пароль для пользователя базы данных.
WP_ADMIN_EMAIL=admin@example.com     # Электронная почта администратора WordPress.
WP_ADMIN_USER=admin                  # Имя администратора WordPress.
WP_ADMIN_PASSWORD=admin_password123  # Пароль администратора WordPress.
DOMAIN_NAME=aliud.ru                 # Имя домена.
HTTP_PORT=8080                       # Порт для wordpress.
PYTHON_SERVER_PORT=8000              # Порт для сервера на Python.
[root@Zero wordpress_nginx_postgres_setup]# docker exec -it grafana grafana-cli admin reset-admin-password admin_password123
Deprecation warning: The standalone 'grafana-cli' program is deprecated and will be removed in the future. Please update all uses of 'grafana-cli' to 'grafana cli'
INFO [01-15|11:00:06] Starting Grafana                         logger=settings version=11.4.0 commit=b58701869e1a11b696010a6f28bd96b68a2cf0d0 branch=HEAD compiled=2025-01-15T11:00:06Z
INFO [01-15|11:00:06] Config loaded from                       logger=settings file=/usr/share/grafana/conf/defaults.ini
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_PATHS_DATA=/var/lib/grafana"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_PATHS_LOGS=/var/log/grafana"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_PATHS_PLUGINS=/var/lib/grafana/plugins"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_PATHS_PROVISIONING=/etc/grafana/provisioning"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_DATABASE_TYPE=postgres"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_DATABASE_HOST=db:5432"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_DATABASE_NAME=wordpress_db"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_DATABASE_USER=wordpress_user"
INFO [01-15|11:00:06] Config overridden from Environment variable logger=settings var="GF_DATABASE_PASSWORD=*********"
INFO [01-15|11:00:06] Target                                   logger=settings target=[all]
INFO [01-15|11:00:06] Path Home                                logger=settings path=/usr/share/grafana
INFO [01-15|11:00:06] Path Data                                logger=settings path=/var/lib/grafana
INFO [01-15|11:00:06] Path Logs                                logger=settings path=/var/log/grafana
INFO [01-15|11:00:06] Path Plugins                             logger=settings path=/var/lib/grafana/plugins
INFO [01-15|11:00:06] Path Provisioning                        logger=settings path=/etc/grafana/provisioning
INFO [01-15|11:00:06] App mode production                      logger=settings
INFO [01-15|11:00:06] FeatureToggles                           logger=featuremgmt pinNavItems=true influxdbBackendMigration=true annotationPermissionUpdate=true lokiQueryHints=true awsAsyncQueryCaching=true autoMigrateXYChartPanel=true transformationsRedesign=true publicDashboards=true openSearchBackendFlowEnabled=true panelMonitoring=true promQLScope=true cloudWatchNewLabelParsing=true addFieldFromCalculationStatFunctions=true transformationsVariableSupport=true publicDashboardsScene=true dashgpt=true alertingSimplifiedRouting=true topnav=true cloudWatchRoundUpEndTime=true lokiQuerySplitting=true groupToNestedTableTransformation=true notificationBanner=true accessControlOnCall=true lokiMetricDataplane=true dashboardSceneForViewers=true prometheusAzureOverrideAudience=true logRowsPopoverMenu=true alertingNoDataErrorExecution=true managedPluginsInstall=true kubernetesPlaylists=true logsContextDatasourceUi=true formatString=true lokiStructuredMetadata=true angularDeprecationUI=true tlsMemcached=true prometheusMetricEncyclopedia=true exploreMetrics=true dashboardScene=true prometheusConfigOverhaulAuth=true recoveryThreshold=true correlations=true cloudWatchCrossAccountQuerying=true logsInfiniteScrolling=true dashboardSceneSolo=true logsExploreTableVisualisation=true ssoSettingsApi=true nestedFolders=true alertingInsights=true dataplaneFrontendFallback=true recordedQueriesMulti=true
INFO [01-15|11:00:06] Connecting to DB                         logger=sqlstore dbtype=postgres
INFO [01-15|11:00:06] Locking database                         logger=migrator
INFO [01-15|11:00:06] Starting DB migrations                   logger=migrator
INFO [01-15|11:00:06] migrations completed                     logger=migrator performed=0 skipped=611 duration=847.343µs
INFO [01-15|11:00:06] Unlocking database                       logger=migrator
INFO [01-15|11:00:07] Envelope encryption state                logger=secrets enabled=true current provider=secretKey.v1

Admin password changed successfully ✔


```

### Настройка интеграции 

– Заходим в веб-итерфейс Grafana по адресу http://ip_сервера:3000  
– Вводим имя пользователя admin и пароль, который установили (в .env)

Добавление источника данных:

– Переходим в раздел Connections в боковом меню;
– Добавляем источник данных --> Add data source;
– Выбираем PostgreSQL из списка доступных источников данных.

Вводим параметры подключения:

Host: db:5432
Database: wordpress_db
User: wordpress_user
Password: secure_password123

Далее --> Save & Test, чтобы проверить подключение.

