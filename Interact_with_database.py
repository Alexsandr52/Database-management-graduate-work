#!/usr/bin/env python3.12

import pymysql

import pymysql

# Параметры подключения к базе данных
DB_HOST = '82.97.249.199'
DB_USER = 'gen_user'
DB_PASSWORD = 'h2d@N:i?9tSZoW'
DB_NAME = 'graduate_work_database'


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

def main():
    # Установление соединения с базой данных
    connection = connect_to_database()
    if connection:
        # Пример данных для добавления
        data_to_insert = {'value1': 1, 'value2': 1, 'value3': 1}
        # Добавление записи в базу данных
        insert_data(connection, ['first_name', 'last_name', 'email', 'phone_number', 'password', 'other_personal_data', 'other_doctor_data'], ['Александр', 'Полянский', 'ak.polyanskiy@gmail.com', 79880005886, '1123', '', ''],'Users')
        # Получение и вывод всех записей из базы данных
        fetch_records(connection, 'Users')
        # Закрытие соединения с базой данных
        connection.close()

if __name__ == "__main__":
    main()
