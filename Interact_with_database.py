#!/usr/bin/env python3.12

import pymysql

import pymysql

# Параметры подключения к базе данных
DB_HOST = '82.97.249.199'
DB_USER = 'gen_user'
DB_PASSWORD = 'h2d@N:i?9tSZoW'
DB_NAME = 'default_db'

MYSQL_HOST='147.45.144.66'
MYSQL_PORT='3306'
MYSQL_USER='gen_user'
MYSQL_PASSWORD='{\+$!RGM1INJ)V'
MYSQL_DBNAME='default_db'

def connect_to_database():
    try:
        # Подключение к базе данных
        connection = pymysql.connect(host=DB_HOST,
                                     user=DB_USER,
                                     password=DB_PASSWORD,
                                     database=DB_NAME,
                                     cursorclass=pymysql.cursors.DictCursor)
        print("Соединение с базой данных успешно установлено.")
        return connection
    except Exception as e:
        print("Ошибка при подключении к базе данных:", e)

def insert_record(connection, data):
    try:
        # Создание объекта курсора
        with connection.cursor() as cursor:
            # SQL запрос для вставки записи
            sql = "INSERT INTO test (id, diw, do, doi) VALUES (%s, %s, %s, %s)"
            # Выполнение SQL запроса с передачей данных
            cursor.execute(sql, (data['value1'], data['value2'], data['value3'], 1))
        # Подтверждение изменений в базе данных
        connection.commit()
        print("Запись успешно добавлена в базу данных.")
    except Exception as e:
        print("Ошибка при добавлении записи в базу данных:", e)

def fetch_records(connection):
    try:
        with connection.cursor() as cursor:
            # SQL запрос для выборки всех записей
            sql = "SELECT * FROM test"
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
        insert_record(connection, data_to_insert)
        # Получение и вывод всех записей из базы данных
        fetch_records(connection)
        # Закрытие соединения с базой данных
        connection.close()

if __name__ == "__main__":
    main()
