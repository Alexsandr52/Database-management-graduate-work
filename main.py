from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, Response, request, jsonify
from Interact_with_database import *
from datetime import timedelta
import json

app = Flask(__name__)
# Настройка секретного ключа для подписи токенов
app.config['JWT_SECRET_KEY'] = 'super-secret'
app.config['JSON_AS_ASCII'] = False
jwt = JWTManager(app)

@app.route('/connection', methods=['GET'])
def check_connection():
    try: 
        connection = connect_to_database()
        print(connection)
    except:
        print('bad')
    
    return jsonify({'error': 'SWR'}), 501

# Получение токена
# curl -d '{"login":"Alex@gmail.com", "password":"12345"}' -H "Content-Type: application/json" -X POST http://localhost:8080/login
@app.route('/login', methods=['POST'])
def login():
    try:
        login = request.json.get('login', None)
        password = request.json.get('password', None)
        
        connection = connect_to_database()
        user = authenticate_user(connection, login, password)
        
        if user['role_id'] == None: 
            connection = connect_to_database()
            set_user_role(connection, user['id'], 2)

        if user != None:
            expires = timedelta(days=3)
            access_token = create_access_token(identity=user, expires_delta=expires)
            return jsonify(access_token=access_token), 200
        
        raise
    
    except:
        res = json.dumps({'msg': 'Неверное имя пользователя или пароль'}, ensure_ascii=False).encode('utf8')
        return Response(res, status=401)    

# Регистрация в приложении
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        response = json.dumps({'error': 'No data provided'}, ensure_ascii=False).encode('utf8')
    
    connection = connect_to_database()
    result = register_user(connection, **data)

    if result:
        response = json.dumps({'message': 'Успешно'}, ensure_ascii=False).encode('utf8')
    else:
        response = json.dumps({'error': 'Пользователь с таким номером или почтой уже существует'}, ensure_ascii=False).encode('utf8')

    return Response(response=response, status=200)

# Получить уведы для пользователя
@app.route('/notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    connection = connect_to_database()
    notifications = get_notifications_by_user_id(connection, current_user['id'])
    for notif in notifications: notif['notification_time'] = str(notif['notification_time'])
    res = json.dumps(notifications, ensure_ascii=False).encode('utf8')
    return Response(res, status=200)

# Отправить изображение как врач или пользователь
@app.route('/sendimagebyid', methods=['POST'])
@jwt_required()
def send_img():
    current_user = get_jwt_identity()
    print(current_user)
    if current_user['role_id'] == 2:
        patient_id = current_user['id']
    elif current_user['role_id'] in [1, 3]:
        patient_id = request.form.get('patient_id')
        if not patient_id:
            return jsonify({'error': 'Patient ID is required for doctors'}), 400
    else:
        return jsonify({'error': 'Permission denied'}), 403

    # Получаем данные изображения из запроса
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image = request.files['image']

    # Загружаем изображение на сервер
    image_url = upload_image_to_bucket(image)
    ai_response = upload_to_neural_network(image_url)

    # Сохраняем информацию об изображении в базу данных
    connection = connect_to_database()
    upload_image(connection, patient_id, image_url)

    return jsonify({'image_url': image_url, 'ai_response': ai_response}), 200

# Получение изображений как для пациента так и врача
@app.route('/imagebyid', methods=['GET', 'POST'])
@jwt_required()
def get_image_info_by_id():
    current_user = get_jwt_identity()
    connection = connect_to_database()
    print(current_user)
    if current_user['role_id'] == 2:
        data = get_image_info_by_patient_id(connection, current_user['id'])
    elif current_user['role_id'] in [1, 3] and request.method == 'POST':
        patient_id = request.get_json().get('patient_id')  
        data = get_image_info_by_patient_id(connection, patient_id)
    else:
        data = 'Что-то не так'

    if type(data) != str:
        for img in data: img['upload_date'] = str(img['upload_date'])

    data = json.dumps(data, ensure_ascii=False).encode('utf8')
    return Response(data, status=200)

# Обновление статуса
@app.route('/update_image', methods=['POST'])
@jwt_required()
def update_image():
    current_user = get_jwt_identity()
    if current_user['role_id'] != 1:  # Предположим, что только доктор может обновлять информацию об изображении
        return jsonify({'error': 'Permission denied'}), 403

    # Получаем данные из тела запроса
    image_id = request.json.get('image_id')
    processing_status = request.json.get('processing_status')

    if not all([image_id, processing_status]):
        return jsonify({'error': 'Both image_id and processing_status are required'}), 400

    connection = connect_to_database()
    try:
        result = update_image_info(connection, image_id, processing_status)
        return Response(json.dumps({'message': result}, ensure_ascii=False).encode('utf8'), status=200)
    except Exception as e: return jsonify({'error': str(e)}), 500

@app.route('/patients_by_doctor', methods=['GET'])
@jwt_required()
def patients_by_doctor():
    current_user = get_jwt_identity()
    if current_user['role_id'] != 1:
        return jsonify({'error': 'Permission denied'}), 403

    doctor_id = current_user['id']

    connection = connect_to_database()
    try:
        patients_ids = get_patients_by_doctor_id(connection, doctor_id)
        patients_array = [patient_id['patient_id'] for patient_id in patients_ids]
        return jsonify({'patients':patients_array}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)