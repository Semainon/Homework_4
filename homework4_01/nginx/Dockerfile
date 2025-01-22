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
