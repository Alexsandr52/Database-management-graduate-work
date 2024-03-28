-- Пользователи
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(10) UNIQUE,
    password VARCHAR(255) NOT NULL,
    other_personal_data TEXT,
    other_doctor_data TEXT
    -- CHECK (phone_number >= 7000000000 AND phone_number <= 7999999999) -- Пример ограничения диапазона для России
);

-- Роли
CREATE TABLE Roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Сопоставления пользователя и роли (Решает вопрос если пользователь и врач и пациент)
CREATE TABLE UserRoles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY(user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (role_id) REFERENCES Roles(id)
);

-- Медецинские изображения
CREATE TABLE Images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    image_data LONGBLOB NOT NULL, -- Здесь предполагается хранение байтового представления
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status ENUM('in processing', 'processed', 'waiting') NOT NULL DEFAULT 'waiting',
    FOREIGN KEY (patient_id) REFERENCES Users(id)
);

-- Результаты анализа по изображению
CREATE TABLE AnalysisResults (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    result_data TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES Images(id)
);

-- Доктор и его пациент (решает вопрос возможности доступа нескольких докторов к одному изображению)
CREATE TABLE DoctorPatient (
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    PRIMARY KEY (doctor_id, patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Users(id),
    FOREIGN KEY (patient_id) REFERENCES Users(id)
);

-- Уведомления для пользователей
CREATE TABLE UserNotifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Текст уведомлений
CREATE TABLE NotificationInfo (
    notification_id INT NOT NULL,
    notification_text TEXT,
    notification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    FOREIGN KEY (notification_id) REFERENCES UserNotifications(notification_id)
);

-- Сессии для подключения
CREATE TABLE UserSessions (
    session_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token VARCHAR(64) NOT NULL,
    expiry_time TIMESTAMP NOT NULL,
    UNIQUE (session_token),  -- Гарантирует уникальность токена сеанса
    INDEX (expiry_time),  -- Индекс для быстрого поиска устаревших сеансов
    FOREIGN KEY (user_id) REFERENCES Users(id)
);
