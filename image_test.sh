#!/bin/bash

# Получение токена аутентификации
TOKEN=$(curl -X POST -H "Content-Type: application/json" -d '{"login":"ex@gmail.com", "password":"1234567"}' http://localhost:8080/login | jq -r '.access_token')

# Проверка токена
if [[ -z "$TOKEN" ]]; then
    echo "Не удалось получить токен"
    exit 1
fi

# Проверка /upload_image с использованием токена
# curl -X POST \
#   -H "Authorization: Bearer $TOKEN" \
#   -F "image=@imgs/IMG0004320.jpg" \
#   http://localhost:8080/sendimagebyid

curl -X GET \
  -H "Authorization: Bearer $TOKEN" \
  http://localhost:8080/imagebyid


