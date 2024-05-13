# from Interact_with_database import *
# from faker import Faker

# fake = Faker()

# # Создаем 10 случайных пользователей
# for _ in range(10):
#     connection = connect_to_database()
#     first_name = fake.first_name()
#     last_name = fake.last_name()
#     email = fake.email()
#     phone = fake.phone_number()
#     password = fake.password(length=10, special_chars=True, digits=True, upper_case=True, lower_case=True)
#     personal_data = fake.text()

#     register_user(connection, first_name, last_name, email, phone, password, personal_data)

# # Создаем ролей
# # Доктор
# connection = connect_to_database()
# create_new_role(connection, 'doctor')

# # Студент
# connection = connect_to_database()
# create_new_role(connection, 'student')

# # Пациент
# connection = connect_to_database()
# create_new_role(connection, 'patient')

# connection = connect_to_database()
# print(get_all_roles(connection))

# # Добавляем пользователям роли
# # Получаем список всех ролей
# connection = connect_to_database()
# roles = get_all_roles(connection)
# # Получаем список всех пользователей
# connection = connect_to_database()
# users = get_all_users(connection)

# # Проходим по каждому пользователю и устанавливаем ему случайную роль
# for user in users:
#     connection = connect_to_database()
#     # Случайно выбираем роль из списка ролей
#     random_role = random.choice(roles)
#     # Получаем ID пользователя и ID новой роли
#     user_id = user['id']
#     new_role_id = random_role['id']
#     # Устанавливаем пользователю новую роль
#     set_user_role(connection, user_id, new_role_id)

# # Привязываем врачей к пациентам
# # Получаем список всех врачей
# connection = connect_to_database()
# doctors = get_users_by_role(connection, role_name='doctor')
# # Получаем список всех пациентов
# connection = connect_to_database()
# patients = get_users_by_role(connection, role_name='patient')

# # Перемешиваем список пациентов
# random.shuffle(patients)

# # Проходим по каждому врачу и назначаем ему пациента из перемешанного списка пациентов
# for i, doctor in enumerate(doctors):
#     connection = connect_to_database()
#     # Получаем ID врача и ID пациента
#     doctor_id = doctor['id']
#     patient_id = patients[i % len(patients)]['id']  # Используем остаток от деления для циклического выбора пациентов
#     # Добавляем запись в таблицу DoctorPatient
#     assign_patient_to_doctor(connection, doctor_id, patient_id)

# # Загружаю изобраение для всех пациентов
# # Путь к изображению
# image_path = 'images/images.png'
# # Загружаем изображение в виде байтовой строки
# image_data = encode_image_to_bytes(image_path)

# # Получаем список всех пациентов из базы данных
# connection = connect_to_database()
# patients = get_users_by_role(connection, role_name='patient')

# # Загружаем изображение для каждого пациента
# for patient in patients:
#     connection = connect_to_database()
#     patient_id = patient['id']
#     upload_image(connection, patient_id, image_data)

# # Смена статуса
# # Меняем статус изображения с ID=1
# connection = connect_to_database()
# update_image_info(connection, image_id=1, processing_status='in processing')

# # Меняем статус изображения с ID=2
# connection = connect_to_database()
# update_image_info(connection, image_id=2, processing_status='processed')
