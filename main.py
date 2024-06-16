from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask import Flask, Response, request, jsonify
from Interact_with_database import *
from datetime import timedelta
import json
import re

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
        connection.close()
    except Exception as e:
        print(f'bad {e}')
    
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
    if current_user['role_id'] == 2:
        patient_id = current_user['id']
    elif current_user['role_id'] in [1, 3]:
        patient_id = request.form.get('patient_id')
        if not patient_id:
            return jsonify({'error': 'Patient ID is required for doctors'}), 400
    else:
        return jsonify({'error': 'Permission denied'}), 403
    # patient_id = 1
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    image = request.files['image']


    # Загружаем изображение на сервер
    image.seek(0)
    ai_response = upload_to_neural_network(image)
    
    boxes = ai_response.get('boxes', [])        
    image.seek(0)
    image_with_boxes = draw_boxes(image, boxes)

    image_url = upload_image_to_bucket(image_with_boxes)

    # Сохраняем информацию об изображении в базу данных
    connection = connect_to_database()
    upload_image(connection, patient_id, image_url)

    connection = connect_to_database()
    data = get_image_info_by_patient_id(connection, patient_id)
    
    gpt_comment = ''

    if ai_response['boxes'] != []:
        try: part = ai_response['results']    
        except: part = None

        gpt_comment = make_comment(is_fructed=True, part=part)["result"]["alternatives"][0]["message"]["text"]
        text_without_brackets = re.sub(r'\[.*?\]', '', gpt_comment)
        gpt_comment = text_without_brackets.replace('**', '')
        gpt_comment = gpt_comment.replace('*', '')

    if type(data) != str:
        img_id = data[-1]['id']

        connection = connect_to_database()
        save_analysis_results(connection, img_id, gpt_comment, str(ai_response))

    connection = connect_to_database()
    create_new_notification(connection, user_id=patient_id)
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

    data = json.dumps(data[::-1], ensure_ascii=False).encode('utf8')
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

# Получение информации о пациенте по ID
@app.route('/patient_info', methods=['POST'])
@jwt_required()
def get_patient_info():
    try:
        current_user = get_jwt_identity()
        if current_user['role_id'] not in [1, 3]:
            return jsonify({'error': 'Unauthorized access'}), 403

        patient_id = request.get_json().get('patient_id')
        if not patient_id:
            return jsonify({'error': 'patient_id is required'}), 400

        connection = connect_to_database()
        patient_info = get_patient_info_by_id(connection, patient_id)
        return Response(response=json.dumps(patient_info, ensure_ascii=False).encode('utf8'), status=200)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Получение новостей
@app.route('/news', methods=['GET'])
def get_news():
    try:
        connection = connect_to_database()
        res = get_all_news(connection)
        for news in res: news['news_time'] = str(news['news_time'])
        return Response(response=json.dumps(res, ensure_ascii=False).encode('utf8'), status=200)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/user_settings', methods=['POST'])
@jwt_required()
def change_user():
    try:
        user_id = get_jwt_identity()['id']
        data = request.get_json()
        connection = connect_to_database()
        response = update_user_info(
            connection,
            user_id,
            new_first_name=data.get('new_first_name'),
            new_last_name=data.get('new_last_name'),
            new_email=data.get('new_email'),
            new_phone_number=data.get('new_phone_number'),
            new_personal_data=data.get('new_personal_data')
        )
        return Response(response=json.dumps({'response': response}, ensure_ascii=False).encode('utf8'), status=200)
    except Exception as e:
        return jsonify({'error': f'Произошла ошибка: {str(e)}'})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)
