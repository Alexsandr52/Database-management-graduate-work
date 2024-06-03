#!/bin/bash

# URL для сервера Flask
BASE_URL="http://localhost:8080"

# Регистрация нового пользователя
echo "Регистрация нового пользователя..."
register_response=$(curl -s -d '{"last_name":"Tester", "first_name":"Tester","email":"test_user@gmail.com", "password":"password123", "role_id":2}' \
                      -H "Content-Type: application/json" \
                      -X POST $BASE_URL/register)
echo "Ответ на регистрацию: $register_response"

# Логин пользователя и получение токена
echo "Логин пользователя..."
login_response=$(curl -s -d '{"login":"test_user@gmail.com", "password":"password123"}' \
                    -H "Content-Type: application/json" \
                    -X POST $BASE_URL/login)
access_token=$(echo $login_response | jq -r '.access_token')
echo "Ответ на логин: $login_response"
echo "Полученный токен: $access_token"

# Получение уведомлений
echo "Получение уведомлений..."
notifications_response=$(curl -s -H "Authorization: Bearer $access_token" \
                           -X GET $BASE_URL/notifications)
echo "Ответ на получение уведомлений: $notifications_response"

# Отправка изображения
echo "Отправка изображения..."
send_image_response=$(curl -s -H "Authorization: Bearer $access_token" \
                        -F "image=@imgs/IMG0004349.jpg" \
                        -X POST $BASE_URL/sendimagebyid)
echo "Ответ на отправку изображения: $send_image_response"

# Получение изображений по ID
echo "Получение изображений по ID..."
get_images_response=$(curl -s -H "Authorization: Bearer $access_token" \
                        -X GET $BASE_URL/imagebyid)
echo "Ответ на получение изображений: $get_images_response"

# Обновление статуса изображения
echo "Обновление статуса изображения..."
update_image_response=$(curl -s -H "Authorization: Bearer $access_token" \
                          -d '{"image_id":1, "processing_status":"processed"}' \
                          -H "Content-Type: application/json" \
                          -X POST $BASE_URL/update_image)
echo "Ответ на обновление статуса изображения: $update_image_response"

# Получение списка пациентов для доктора
echo "Получение списка пациентов для доктора..."
patients_response=$(curl -s -H "Authorization: Bearer $access_token" \
                     -X GET $BASE_URL/patients_by_doctor)
echo "Ответ на получение списка пациентов: $patients_response"
