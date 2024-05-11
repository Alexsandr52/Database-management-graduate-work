from flask import Flask, Response, request, jsonify
from datetime import timedelta
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import json
from Interact_with_database import *

app = Flask(__name__)
# Настройка секретного ключа для подписи токенов
app.config['JWT_SECRET_KEY'] = 'super-secret'  # Измените на свой секретный ключ
app.config['JSON_AS_ASCII'] = False
jwt = JWTManager(app)

# Получение токена
@app.route('/login', methods=['POST'])
def login():
    try:
        login = request.json.get('login', None)
        password = request.json.get('password', None)
        
        connection = connect_to_database()
        user = authenticate_user(connection, login, password)

        if user != {}:
            expires = timedelta(days=3)
            access_token = create_access_token(identity=user, expires_delta=expires)
            return jsonify(access_token=access_token), 200
    
    except:
            return jsonify({'msg': 'Неверное имя пользователя или пароль'}), 401    
# Регистрация в приложении
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No data provided'}), 400
    
    connection = connect_to_database()
    result = register_user(connection, **data)

    if result:
        return jsonify({'message': 'User registered successfully'}), 201
    else:
        return jsonify({'error': 'User with that email or phone number already exists'}), 400
# Получить уведы для пользователя
@app.route('/get_notifications', methods=['GET'])
@jwt_required()
def get_notifications():
    current_user = get_jwt_identity()
    connection = connect_to_database()
    notifications = get_notifications_by_user_id(connection, current_user['id'])
    for notif in notifications: notif['notification_time'] = str(notif['notification_time'])
    res = json.dumps(notifications, ensure_ascii=False).encode('utf8')
    return Response(res, status=200)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)