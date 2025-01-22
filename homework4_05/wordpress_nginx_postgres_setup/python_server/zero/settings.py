import os
from pathlib import Path

# Определяем базовую директорию проекта
BASE_DIR = Path(__file__).resolve().parent.parent

# Секретный ключ
SECRET_KEY = os.environ.get('SECRET_KEY')

# Режим отладки
DEBUG = os.environ.get('DEBUG', 'True') == 'True'

# Разрешенные хосты
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', '').split(',')

# Приложения
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'zero',  # Наше приложение
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# URL конфигурация
ROOT_URLCONF = 'zero.urls'

# Настройки шаблонов
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'zero/templates')],  # Укажите путь к вашей папке templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# База данных
# DATABASES = {
        # 'default': {
        # 'ENGINE': 'django.db.backends.postgresql',
        # 'NAME': os.environ.get('PYTHON_DB_NAME'),
        # 'USER': os.environ.get('PYTHON_DB_USER'),
        # 'PASSWORD': os.environ.get('PYTHON_DB_PASSWORD'),
        # 'HOST': os.environ.get('DB_HOST', 'db'),
        # 'PORT': os.environ.get('DB_PORT', '5432'),
    # }
 #}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',  # Путь к файлу базы данных
    }
}


LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

# Статические файлы
STATIC_URL = '/static/'

# Получение переменных окружения для суперюзера
SUPERUSER_USERNAME = os.environ.get('SUPERUSER_USERNAME')
SUPERUSER_PASSWORD = os.environ.get('SUPERUSER_PASSWORD')

