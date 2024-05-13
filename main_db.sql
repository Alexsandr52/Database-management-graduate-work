SET FOREIGN_KEY_CHECKS = 0;

-- Пользователи
DROP TABLE IF EXISTS Users;
CREATE TABLE Users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    phone_number VARCHAR(10) UNIQUE,
    password VARCHAR(255) NOT NULL,
    other_personal_data TEXT
);

-- Роли
DROP TABLE IF EXISTS Roles;
CREATE TABLE Roles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

-- Сопоставления пользователя и роли (Решает вопрос если пользователь и врач и пациент)
DROP TABLE IF EXISTS UserRoles;
CREATE TABLE UserRoles (
    user_id INT NOT NULL,
    role_id INT NOT NULL,
    PRIMARY KEY(user_id, role_id),
    FOREIGN KEY (user_id) REFERENCES Users(id),
    FOREIGN KEY (role_id) REFERENCES Roles(id)
);

-- Медецинские изображения
DROP TABLE IF EXISTS Images;
CREATE TABLE Images (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    image_data TEXT NOT NULL, -- Здесь предполагается хранение байтового представления
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    processing_status ENUM('in processing', 'processed', 'waiting') NOT NULL DEFAULT 'waiting',
    FOREIGN KEY (patient_id) REFERENCES Users(id)
);

-- Результаты анализа по изображению
DROP TABLE IF EXISTS AnalysisResults;
CREATE TABLE AnalysisResults (
    id INT AUTO_INCREMENT PRIMARY KEY,
    image_id INT NOT NULL,
    result_data TEXT,
    analysis_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (image_id) REFERENCES Images(id)
);

-- Доктор и его пациент (решает вопрос возможности доступа нескольких докторов к одному изображению)
DROP TABLE IF EXISTS DoctorPatient;
CREATE TABLE DoctorPatient (
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    PRIMARY KEY (doctor_id, patient_id),
    FOREIGN KEY (doctor_id) REFERENCES Users(id),
    FOREIGN KEY (patient_id) REFERENCES Users(id)
);

-- Уведомления для пользователей
DROP TABLE IF EXISTS UserNotifications;
CREATE TABLE UserNotifications (
    notification_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES Users(id)
);

-- Текст уведомлений
DROP TABLE IF EXISTS NotificationInfo;
CREATE TABLE NotificationInfo (
    notification_id INT NOT NULL,
    notification_text TEXT,
    notification_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (notification_id),
    FOREIGN KEY (notification_id) REFERENCES UserNotifications(notification_id)
);


SET FOREIGN_KEY_CHECKS = 1;