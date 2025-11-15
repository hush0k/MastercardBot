# Frontend Dockerfile с nginx
FROM nginx:alpine

# Копирование статических файлов
COPY index.html /usr/share/nginx/html/
COPY style.css /usr/share/nginx/html/
COPY app.js /usr/share/nginx/html/
COPY assets/ /usr/share/nginx/html/assets/

# Копирование конфигурации nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose порт
EXPOSE 80

# Healthcheck
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

# Nginx запускается автоматически