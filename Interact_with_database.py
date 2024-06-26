#!/usr/bin/env python3.12
from decouple import config
import hashlib
import datetime
import pymysql
import requests
import secrets
import string
import random
import cv2
from io import BytesIO
from PIL import Image
import numpy as np
import os

DB_HOST = config('DB_HOST')
DB_USER = config('DB_USER')
DB_PASSWORD = config('DB_PASSWORD')
DB_NAME = config('DB_NAME')
base_id = config('BASE_ID')
api_key = config('API_KEY')

# Подключение к базе данных
def connect_to_database():
    try:
        connection = pymysql.connect(host=DB_HOST, user=DB_USER,
                                     password=DB_PASSWORD,
                                     database=DB_NAME,
                                     cursorclass=pymysql.cursors.DictCursor)
        # print('Соединение с базой данных успешно установлено.')
        return connection
    
    except Exception as e: print('Ошибка при подключении к базе данных:', e)
    
    return None

# Вспомогательные функции
# Достать всее из таблицы по имени
def fetch_records(connection, table):
    try:
        with connection.cursor() as cursor:
            # SQL запрос для выборки всех записей
            sql = f'SELECT * FROM {table}'
            # Выполнение SQL запроса
            cursor.execute(sql)
            # Получение результатов запроса
            result = cursor.fetchall()
            # Вывод результатов
            print('Результаты запроса:')
            for row in result:
                print(row)
    except Exception as e:
        print('Ошибка при выполнении запроса к базе данных:', e)

# Учетные записи
# Функция для смены пароля пользователя
def change_password(connection, user_id, new_password):
    try:
        with connection.cursor() as cursor:
            # Обновляем пароль пользователя
            sql_update_password = 'UPDATE Users SET password = %s WHERE id = %s'
            cursor.execute(sql_update_password, (new_password, user_id))
            connection.commit()

            return 'Пароль успешно изменен'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Генерация временного пароля
def generate_temp_password(length=8):
    characters = string.ascii_letters + string.digits
    temp_password = ''.join(random.choice(characters) for i in range(length))
    return temp_password
# Отправка временного пароля по электронной почте
def send_temp_password_via_email(email, temp_password):
    # Отправка временного пароля по электронной почте (здесь должен быть код для отправки почты)
    print(f'Отправка временного пароля {temp_password} на {email}')
# Функция для обновления информации о пользователе
def update_user_info(connection, user_id, new_first_name=None, new_last_name=None, new_email=None, new_phone_number=None, new_personal_data=None):
    try:
        with connection.cursor() as cursor:
            update_values = {}
            if new_first_name is not None:
                update_values['first_name'] = new_first_name
            if new_last_name is not None:
                update_values['last_name'] = new_last_name
            if new_email is not None:
                update_values['email'] = new_email
            if new_phone_number is not None:
                update_values['phone_number'] = new_phone_number
            if new_personal_data is not None:
                update_values['other_personal_data'] = new_personal_data

            if update_values:
                sql_update_info = 'UPDATE Users SET ' + ', '.join(f"{key} = %s" for key in update_values.keys()) + ' WHERE id = %s'
                query_values = list(update_values.values()) + [user_id]
                cursor.execute(sql_update_info, tuple(query_values))
                connection.commit()

            return 'Информация о пользователе успешно обновлена'
    finally:
        connection.close()

# Функция для получения списка всех пользователей
def get_all_users(connection): 
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM Users'
            cursor.execute(sql)
            users = cursor.fetchall()
            return users
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

# Уведомления
# Функция для получения уведомлений по ID пользователя
def get_notifications_by_user_id(connection, user_id):
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM UserNotifications WHERE user_id = %s'
            cursor.execute(sql, (user_id,))
            notifications = cursor.fetchall()
            return notifications
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Создавать уведы
def create_new_notification(connection, user_id, notification_title=None, notification_text=None):
    if notification_title == None: notification_title = 'Ваши медицинские анализы готовы!'
    if notification_text == None: notification_text = '''Хорошие новости! Ваши медицинские анализы уже доступны. Мы завершили обработку результатов и теперь вы можете получить информацию о вашем состоянии здоровья.\nЗабота о вашем здоровье — наш главный
                                                        приоритет.'''
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли пользователь с данным ID
            sql_check_user = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql_check_user, (user_id,))
            existing_user = cursor.fetchone()

            if not existing_user:
                return 'Пользователь с таким ID не существует'

            # Создаем новое уведомление
            sql_create_notification = '''
                INSERT INTO UserNotifications (user_id, notification_title, notification_text)
                VALUES (%s, %s, %s)
            '''
            cursor.execute(sql_create_notification, (user_id, notification_title, notification_text))
            connection.commit()

            return 'Новое уведомление успешно создано'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

#Взаимодействие с ролями 
# Функция для получения списка всех ролей
def get_all_roles(connection):
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM Roles'
            cursor.execute(sql)
            roles = cursor.fetchall()
            return roles
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для создания новой роли
def create_new_role(connection, role_name):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли роль с таким же именем
            sql_check_role = 'SELECT * FROM Roles WHERE name = %s'
            cursor.execute(sql_check_role, (role_name,))
            existing_role = cursor.fetchone()

            if existing_role:
                return 'Роль с таким именем уже существует'

            # Создаем новую роль
            sql_create_role = 'INSERT INTO Roles (name) VALUES (%s)'
            cursor.execute(sql_create_role, (role_name,))
            connection.commit()

            return 'Новая роль успешно создана'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для удаления роли
def delete_role(connection, role_id):
    try:
        with connection.cursor() as cursor:
            # Удаляем роль
            sql_delete_role = 'DELETE FROM Roles WHERE id = %s'
            cursor.execute(sql_delete_role, (role_id,))
            connection.commit()

            return 'Роль успешно удалена'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для изменения роли пользователя
def change_user_role(connection, user_id, new_role_id):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли пользователь с таким ID
            sql_check_user = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql_check_user, (user_id,))
            user = cursor.fetchone()

            if not user:
                return 'Пользователь с указанным ID не найден'

            # Проверяем, существует ли роль с таким ID
            sql_check_role = 'SELECT * FROM Roles WHERE id = %s'
            cursor.execute(sql_check_role, (new_role_id,))
            role = cursor.fetchone()

            if not role:
                return 'Роль с указанным ID не найдена'

            # Обновляем роль пользователя
            sql_update_role = 'UPDATE UserRoles SET role_id = %s WHERE user_id = %s'
            cursor.execute(sql_update_role, (new_role_id, user_id))
            connection.commit()

            return 'Роль пользователя успешно изменена'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Задание роли для пользователя
def set_user_role(connection, user_id, new_role_id=None):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли пользователь с таким ID
            sql_check_user = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql_check_user, (user_id,))
            user = cursor.fetchone()

            if not user:
                return 'Пользователь с указанным ID не найден'

            # Если новый ID роли указан, проверяем его существование
            if new_role_id is not None:
                sql_check_role = 'SELECT * FROM Roles WHERE id = %s'
                cursor.execute(sql_check_role, (new_role_id,))
                role = cursor.fetchone()

                if not role:
                    return 'Роль с указанным ID не найдена'

            # Если новый ID роли указан, устанавливаем его пользователю
            if new_role_id is not None:
                sql_set_role = 'INSERT INTO UserRoles (user_id, role_id) VALUES (%s, %s) ON DUPLICATE KEY UPDATE role_id = %s'
                cursor.execute(sql_set_role, (user_id, new_role_id, new_role_id))
                connection.commit()
                return 'Роль пользователя успешно установлена'
            else:
                return 'Новый ID роли не указан'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Получение пользователей по id
def get_users_by_role(connection, role_name):
    try:
        with connection.cursor() as cursor:
            # Получаем ID роли по ее названию
            cursor.execute('SELECT id FROM Roles WHERE name = %s', (role_name,))
            role_id = cursor.fetchone()

            if not role_id:
                return f'Роль с названием {role_name} не найдена.'

            # Получаем пользователей с указанной ролью
            sql = '''
                SELECT u.*
                FROM Users u
                INNER JOIN UserRoles ur ON u.id = ur.user_id
                INNER JOIN Roles r ON ur.role_id = r.id
                WHERE r.name = %s
            '''
            cursor.execute(sql, (role_name,))
            users = cursor.fetchall()

            if not users:
                return f'Нет пользователей с ролью {role_name}.'

            return users
    except pymysql.Error as e:
        return f'Ошибка при получении пользователей с ролью {role_name}: {e}'
    finally:
        connection.close()

# Взаимодействие с пользователем    
# Аутентификация пользователя по электронной почте или номеру телефона и паролю
def authenticate_user(connection, email_or_phone, password):
    try:
        with connection.cursor() as cursor:
            # Поиск пользователя по электронной почте или номеру телефона и паролю
            sql = 'SELECT Users.id, Users.first_name, Users.last_name, Users.email, UserRoles.role_id FROM Users LEFT JOIN UserRoles ON Users.id = UserRoles.user_id WHERE (Users.email = %s OR Users.phone_number = %s) AND Users.password = %s'
            cursor.execute(sql, (email_or_phone, email_or_phone, password))
            user = cursor.fetchone()

            if user:
                # Получаем роль пользователя
                role_id = user['role_id']
                # Возвращаем данные пользователя и его роль, если он найден
                return {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                    'role_id': role_id
                }
    finally:
        connection.close()
# Функция для регистрации нового пользователя OLD
def register_user(connection, first_name, email, password, last_name=None, phone_number=None, other_personal_data=None,):
    try:
        with connection.cursor() as cursor:
            # Проверяем, что пользователь с такой электронной почтой или номером телефона не существует
            sql = 'SELECT * FROM Users WHERE email = %s OR phone_number = %s'
            cursor.execute(sql, (email, phone_number))
            existing_user = cursor.fetchone()

            if existing_user:
                # Если пользователь уже существует, возвращаем сообщение об ошибке
                return False
            
            else:
                # Добавляем нового пользователя в базу данных
                sql = 'INSERT INTO Users (first_name, last_name, email, phone_number, password, other_personal_data) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (first_name, last_name, email, phone_number, password, other_personal_data))
                connection.commit()
                return True
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для регистрации нового пользователя NEW
def register_user(connection, **kwargs):
    try:
        with connection.cursor() as cursor:
            # Проверяем, что пользователь с такой электронной почтой или номером телефона не существует
            sql = 'SELECT * FROM Users WHERE email = %s OR phone_number = %s'
            cursor.execute(sql, (kwargs.get('email'), kwargs.get('phone_number')))
            existing_user = cursor.fetchone()

            if existing_user:
                # Если пользователь уже существует, возвращаем сообщение об ошибке
                return False
            
            else:
                # Добавляем нового пользователя в базу данных
                sql = 'INSERT INTO Users (first_name, last_name, email, phone_number, password, other_personal_data) VALUES (%s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (
                    kwargs.get('first_name'),
                    kwargs.get('last_name'),
                    kwargs.get('email'),
                    kwargs.get('phone_number'),
                    kwargs.get('password'),
                    kwargs.get('other_personal_data')
                ))
                connection.commit()
                return True
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()


# Функция для привязки пациента к доктору
def assign_patient_to_doctor(connection, doctor_id, patient_id):
    
    try:
        with connection.cursor() as cursor:
            # Проверяем, что доктор и пациент существуют в базе данных
            sql_check_doctor = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql_check_doctor, (doctor_id,))
            doctor = cursor.fetchone()

            if not doctor:
                return 'Доктор с таким идентификатором не найден или не является врачом'

            sql_check_patient = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql_check_patient, (patient_id,))
            patient = cursor.fetchone()

            if not patient:
                return 'Пациент с таким идентификатором не найден или не является пациентом'

            # Проверяем, что связь между доктором и пациентом не существует
            sql_check_relationship = 'SELECT * FROM DoctorPatient WHERE doctor_id = %s AND patient_id = %s'
            cursor.execute(sql_check_relationship, (doctor_id, patient_id))
            existing_relationship = cursor.fetchone()

            if existing_relationship:
                return True

            # Добавляем связь между доктором и пациентом
            sql_insert_relationship = 'INSERT INTO DoctorPatient (doctor_id, patient_id) VALUES (%s, %s)'
            cursor.execute(sql_insert_relationship, (doctor_id, patient_id))
            connection.commit()
            return True
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

# Работа с изображениями       
# Функция для получения информации об изображениях по patient_id
def get_image_info_by_patient_id(connection, patient_id):
    try:
        with connection.cursor() as cursor:
            # Получаем данные об изображениях и их результаты анализа для данного пациента
            sql = '''
            SELECT i.id, i.upload_date, i.processing_status, i.image_data, a.result_data, a.boxes
            FROM Images AS i
            LEFT JOIN AnalysisResults AS a ON i.id = a.image_id
            WHERE i.patient_id = %s
            '''
            cursor.execute(sql, (patient_id,))
            images_info = cursor.fetchall()
            return images_info
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для загрузки изображения для конкретного пациента
def upload_image(connection, patient_id, image_data):
    try:
        with connection.cursor() as cursor:
            # Загружаем изображение для указанного пациента
            sql = 'INSERT INTO Images (patient_id, image_data) VALUES (%s, %s)'
            cursor.execute(sql, (patient_id, image_data))
            connection.commit()
            return True
    except:
        return False
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для получения изображения по его ID
def get_image_by_id(connection, image_id):
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM Images WHERE id = %s'
            cursor.execute(sql, (image_id,))
            image = cursor.fetchone()
            return image
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для обновления информации об изображении (например, статуса обработки)
def update_image_info(connection, image_id, processing_status):
    try:
        with connection.cursor() as cursor:
            sql = 'UPDATE Images SET processing_status = %s WHERE id = %s'
            cursor.execute(sql, (processing_status, image_id))
            connection.commit()
            return 'Информация об изображении успешно обновлена'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для удаления изображения
def delete_image(connection, image_id):
    try:
        with connection.cursor() as cursor:
            sql = 'DELETE FROM Images WHERE id = %s'
            cursor.execute(sql, (image_id,))
            connection.commit()
            return 'Изображение успешно удалено'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Загрузка изображения в бакет
def upload_image_to_bucket(image):
    url = 'https://alexsandr52-img-to-bucket-falsk-243c.twc1.net/upload'
    files = {'image': image}

    try:
        response = requests.post(url, files=files)
        if response.status_code == 200:
            return response.json()['image_url']
        else:
            return None
    except Exception as e:
        print('Error uploading image:', e)
        return None
# Загрузка изображения в ai
def download_image(image_url):
    response = requests.get(image_url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception('Failed to download image')

def upload_to_neural_network(image):
    url = 'https://alexsandr52-yolov8-for-fracture-detection-1d6d.twc1.net/predict'

    try:
        # Отправляем изображение на сервер
        files = {'file': ('image.jpg', image, 'image/jpeg')}
        response = requests.post(url, files=files)
        
        # Проверяем статус ответа
        response.raise_for_status()
        
        return response.json()
    
    except requests.exceptions.RequestException as e:
        return {'error': str(e)}
    except Exception as e:
        return {'error': str(e)}

# Рисует квадраты на изображении на основе предоставленных координат.
def draw_boxes(image, boxes):
    # Преобразуем входное изображение из буфера в формат numpy массива
    np_image = np.frombuffer(image.read(), np.uint8)
    image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)
    
    # Создаем копию изображения для рисования пятен
    overlay = image.copy()
    
    for box in boxes:
        x, y, w, h = box
        center = (int(x-6 + w / 2), int(y-6 + h / 2))
        radius = int(max(w+4, h+4) / 2)  # Радиус круга равен половине большей стороны прямоугольника
        
        # Создаем временное изображение для рисования круга
        temp_image = overlay.copy()
        cv2.circle(temp_image, center, radius, (0, 255, 0), -1)  # -1 заполняет круг
        alpha=0.26
        # Смешиваем временное изображение с исходным
        cv2.addWeighted(temp_image, alpha, overlay, 1 - alpha, 0, overlay)
    
    is_success, buffer = cv2.imencode(".jpg", overlay)
    return BytesIO(buffer)

# Для докторов
def get_patient_info_by_id(connection, patient_id):
    try:
        with connection.cursor() as cursor:
            # SQL запрос для выборки информации о пациенте по ID
            sql = 'SELECT * FROM Users WHERE id = %s'
            cursor.execute(sql, (patient_id,))
            result = cursor.fetchone()
            if result:
                return result
            else:
                return {'error': 'Patient not found'}
    except Exception as e:
        print('Ошибка при выполнении запроса к базе данных:', e)
        return {'error': str(e)}

# Функция для получения списка пациентов, которые привязаны к определенному доктору
def get_patients_by_doctor_id(connection, doctor_id):
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT patient_id FROM DoctorPatient WHERE doctor_id = %s'
            cursor.execute(sql, (doctor_id,))
            patients_ids = cursor.fetchall()
            return patients_ids
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для удаления связи между доктором и пациентом
def delete_relationship(connection, doctor_id, patient_id):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли такая связь
            sql_check_relationship = 'SELECT * FROM DoctorPatient WHERE doctor_id = %s AND patient_id = %s'
            cursor.execute(sql_check_relationship, (doctor_id, patient_id))
            relationship = cursor.fetchone()

            if not relationship:
                return 'Связь между указанным доктором и пациентом не найдена'

            # Удаляем связь
            sql_delete_relationship = 'DELETE FROM DoctorPatient WHERE doctor_id = %s AND patient_id = %s'
            cursor.execute(sql_delete_relationship, (doctor_id, patient_id))
            connection.commit()

            return 'Связь между доктором и пациентом успешно удалена'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

# Работа с таблицей анализ
# Функция для сохранения результатов анализа в базе данных
def save_analysis_results(connection, image_id, result_data, boxes):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли изображение с таким ID
            sql_check_image = 'SELECT * FROM Images WHERE id = %s'
            cursor.execute(sql_check_image, (image_id,))
            image = cursor.fetchone()

            if not image:
                return 'Изображение с указанным ID не найдено'

            # Сохраняем результаты анализа
            sql_save_results = 'INSERT INTO AnalysisResults (image_id, result_data, boxes) VALUES (%s, %s, %s)'
            cursor.execute(sql_save_results, (image_id, result_data, boxes))
            connection.commit()

            return 'Результаты анализа успешно сохранены'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для получения результатов анализа по ID изображения
def get_analysis_results_by_image_id(connection, image_id):
    try:
        with connection.cursor() as cursor:
            sql = 'SELECT * FROM AnalysisResults WHERE image_id = %s'
            cursor.execute(sql, (image_id,))
            results = cursor.fetchone()
            return results
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для обновления результатов анализа
def update_analysis_results(connection, image_id, new_results):
    try:
        with connection.cursor() as cursor:
            # Проверяем, существует ли изображение с таким ID
            sql_check_image = 'SELECT * FROM Images WHERE id = %s'
            cursor.execute(sql_check_image, (image_id,))
            image = cursor.fetchone()

            if not image:
                return 'Изображение с указанным ID не найдено'

            # Обновляем результаты анализа
            sql_update_results = 'UPDATE AnalysisResults SET results = %s WHERE image_id = %s'
            cursor.execute(sql_update_results, (new_results, image_id))
            connection.commit()

            return 'Результаты анализа успешно обновлены'
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

# Админ
# Функция для поиска пользователей по различным критериям
def search_users(connection, criteria):
    try:
        with connection.cursor() as cursor:
            # Формируем SQL-запрос для поиска пользователей
            sql = 'SELECT * FROM Users WHERE '
            conditions = []
            values = []
            for key, value in criteria.items():
                conditions.append(f'{key} = %s')
                values.append(value)
            sql += ' AND '.join(conditions)
            cursor.execute(sql, tuple(values))
            users = cursor.fetchall()
            return users
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
# Функция для поиска изображений по различным критериям
def search_images(connection, criteria):
    try:
        with connection.cursor() as cursor:
            # Формируем SQL-запрос для поиска изображений
            sql = 'SELECT * FROM Images WHERE '
            conditions = []
            values = []
            for key, value in criteria.items():
                conditions.append(f'{key} = %s')
                values.append(value)
            sql += ' AND '.join(conditions)
            cursor.execute(sql, tuple(values))
            images = cursor.fetchall()
            return images
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()         

def get_all_news(connection):
    try:
        with connection.cursor() as cursor:
            # SQL запрос для выборки всех новостей
            sql = 'SELECT * FROM News ORDER BY news_time DESC'
            cursor.execute(sql)
            result = cursor.fetchall()
            if result:
                return result
            else:
                raise {'error': 'No news found'}
    except Exception as e:
        print('Ошибка при выполнении запроса к базе данных:', e)
        raise {'error': str(e)}

def make_comment(part=None, is_fructed=False):
    try:
        part = f"часть тела на снимке - {['рука', 'нога', 'таз', 'плечо'][part]},"
    except:
        part = 'на котором мы не смогли определить часть тела'

    fruc_status = 'перелом' if is_fructed else 'перелом отсутствует'

    prompt = {
        "modelUri": f"gpt://{base_id}/yandexgpt-lite",
        "completionOptions": {
            "stream": False,
            "temperature": 0.6,
            "maxTokens": "600"
        },
        "messages": [
            {
                "role": "system",
                "text": """Ты система, которая пишет комментарии к результатам рентгена, внутри больницы. 
                           Придумай краткий и информативный комментарий к данным, полученным после рентгеновского анализа. 
                           Комментарий должен быть полезен пациенту, но может быть полезен и сотруднику больницы. 
                           Он должен быть кратким и включать наблюдение за наличием или отсутствием перелома, и рекомендуемыми действиями."""
            },
            {
                "role": "user",
                "text": f"Комментарий к результату рентгеновского анализа, {part} {fruc_status}."
            }
        ]
    }

    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Api-Key " + api_key
    }

    response = requests.post(url, headers=headers, json=prompt)
    return response.json()  # Return JSON response

# Сброс бд
# Создать таблицы 
def execute_sql_file(connection, sql_file):
    try:
        with open(sql_file, 'r') as file:
            sql_statements = file.read().split(';')
            with connection.cursor() as cursor:
                for sql_statement in sql_statements:
                    if sql_statement.strip():
                        cursor.execute(sql_statement)
        connection.commit()
        print('SQL-файл успешно выполнен.')
    except pymysql.Error as e:
        print('Ошибка выполнения SQL-файла:', e)
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close() 

# Пересоздать бд
def main():
    connection = connect_to_database()
    execute_sql_file(connection, 'main_db.sql')
    for role in ['doctor', 'patient', 'student']:
        connection = connect_to_database()
        create_new_role(connection, role)
     
if __name__ == '__main__':
    main()
