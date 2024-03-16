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
        print("Соединение с базой данных успешно установлено.")
        return connection
    
    except Exception as e:
        print("Ошибка при подключении к базе данных:", e)
    
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
        print("Запись успешно добавлена в базу данных.")
    except Exception as e:
        print("Ошибка при добавлении записи в базу данных:", e)

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
            print("Результаты запроса:")
            for row in result:
                print(row)
    except Exception as e:
        print("Ошибка при выполнении запроса к базе данных:", e)

def check_login(login):
    pass    

def check_password(login, password):
    pass

def add_image(user_id, img):
    pass

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

if __name__ == "__main__":
    main()
