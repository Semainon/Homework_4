# Используем официальный образ Python
FROM python:3.11-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь проект в контейнер
COPY . .

# Выполняем миграции
#RUN python manage.py migrate

# Запускаем скрипт для создания суперпользователя
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
