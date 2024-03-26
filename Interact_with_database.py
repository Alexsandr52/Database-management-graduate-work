#!/usr/bin/env python3.12

import pymysql
import os
import database_main_insert_varibles as dbv



os.environ['DB_HOST'] = ''
os.environ['DB_USER'] = 'gen_user'
os.environ['DB_PASSWORD'] = 'h2d@N:i?9tSZoW'
os.environ['DB_NAME'] = 'graduate_work_database'

# Параметры подключения к базе данных
DB_HOST = os.getenv('DB_HOST')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_NAME = os.getenv('DB_NAME')


# Подключение к базе данных
def connect_to_database():
    try:
        connection = pymysql.connect(host=DB_HOST, user=DB_USER,
                                     password=DB_PASSWORD,
                                     database=DB_NAME,
                                     cursorclass=pymysql.cursors.DictCursor)
        print('Соединение с базой данных успешно установлено.')
        return connection
    
    except Exception as e: print('Ошибка при подключении к базе данных:', e)
    
    return None

def insert_data(connection, variables, data, table_name):
    try:
        # Создание объекта курсора
        with connection.cursor() as cursor:
            # SQL запрос для вставки записи

            sql = f'INSERT INTO {table_name} ({', '.join(variables)}) VALUES ({', '.join(['%s' for _ in range(len(variables))])})'
            # Выполнение SQL запроса с передачей данных
            cursor.execute(sql, (data))
        # Подтверждение изменений в базе данных
        connection.commit()
        print('Запись успешно добавлена в базу данных.')
    except Exception as e:
        print('Ошибка при добавлении записи в базу данных:', e)

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

# Аутентификация пользователя по электронной почте или номеру телефона и паролю
def authenticate_user(connection, email_or_phone, password):
    try:
        with connection.cursor() as cursor:
            # Поиск пользователя по электронной почте или номеру телефона и паролю
            sql = 'SELECT * FROM Users WHERE (email = %s OR phone_number = %s) AND password = %s'
            cursor.execute(sql, (email_or_phone, email_or_phone, password))
            user = cursor.fetchone()

            if user:
                # Возвращаем данные пользователя, если он найден
                return {
                    'id': user['id'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name'],
                    'email': user['email'],
                }
    finally:
        connection.close()    
    
    return None

# Функция для регистрации нового пользователя
def register_user(connection, first_name, last_name, email, phone_number, password, other_personal_data=None, other_doctor_data=None):
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
                sql = 'INSERT INTO Users (first_name, last_name, email, phone_number, password, other_personal_data, other_doctor_data) VALUES (%s, %s, %s, %s, %s, %s, %s)'
                cursor.execute(sql, (first_name, last_name, email, phone_number, password, other_personal_data, other_doctor_data))
                connection.commit()
                return True
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()
    
    return False

# Функция для привязки пациента к доктору
def assign_patient_to_doctor(connection, doctor_id, patient_id):
    
    try:
        with connection.cursor() as cursor:
            # Проверяем, что доктор и пациент существуют в базе данных
            sql_check_doctor = 'SELECT * FROM Users WHERE id = %s AND other_doctor_data IS NOT NULL'
            cursor.execute(sql_check_doctor, (doctor_id,))
            doctor = cursor.fetchone()

            if not doctor:
                return 'Доктор с таким идентификатором не найден или не является врачом'

            sql_check_patient = 'SELECT * FROM Users WHERE id = %s AND other_personal_data IS NOT NULL'
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

# Функция для получения информации об изображениях по patient_id
def get_image_info_by_patient_id(connection, patient_id):
    try:
        with connection.cursor() as cursor:
            # Получаем все данные об изображениях для данного пациента
            sql = 'SELECT * FROM Images WHERE patient_id = %s'
            cursor.execute(sql, (patient_id,))
            images_info = cursor.fetchall()
            return images_info
    finally:
        # Всегда закрываем соединение, чтобы избежать утечек
        connection.close()

def main():
    # Установление соединения с базой данных
    connection = connect_to_database()
    if connection:
        # Добавление записи в базу данных
        insert_data(connection, dbv.Users, ['Александр', 'Полянский', 'ak.polyanskiy@gmail.com', 79880005506, '1123', '', ''],'Users')
        # Получение и вывод всех записей из базы данных
        fetch_records(connection, 'Users')
        # Закрытие соединения с базой данных
        connection.close()

if __name__ == '__main__':
    main()
