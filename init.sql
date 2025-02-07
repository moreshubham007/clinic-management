-- Create database if not exists
CREATE DATABASE IF NOT EXISTS clinic_db;
USE clinic_db;

-- Create user table
CREATE TABLE IF NOT EXISTS user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(256),
    name VARCHAR(100) NOT NULL,
    role VARCHAR(20) NOT NULL,
    google_id VARCHAR(100) UNIQUE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    address TEXT,
    state VARCHAR(50),
    city VARCHAR(50),
    pin_code VARCHAR(6),
    mobile_number VARCHAR(15),
    date_of_birth DATE,
    aadhar_number VARCHAR(12) UNIQUE,
    patient_number VARCHAR(11) UNIQUE,
    gender VARCHAR(10)
);

-- Create doctor table
CREATE TABLE IF NOT EXISTS doctor (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    specialization VARCHAR(100),
    availability JSON,
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create appointment table
CREATE TABLE IF NOT EXISTS appointment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    datetime DATETIME NOT NULL,
    status VARCHAR(20) DEFAULT 'scheduled',
    notes TEXT,
    remarks TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (doctor_id) REFERENCES doctor(id),
    FOREIGN KEY (patient_id) REFERENCES user(id)
);

-- Create case table
CREATE TABLE IF NOT EXISTS `case` (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    diagnosis TEXT,
    treatment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    show_to_patient BOOLEAN DEFAULT FALSE,
    status VARCHAR(20) DEFAULT 'active',
    FOREIGN KEY (patient_id) REFERENCES user(id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(id)
);

-- Create case_history table
CREATE TABLE IF NOT EXISTS case_history (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_id INT NOT NULL,
    user_id INT NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES `case`(id),
    FOREIGN KEY (user_id) REFERENCES user(id)
);

-- Create question table
CREATE TABLE IF NOT EXISTS question (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    question TEXT,
    answer TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    answered_at DATETIME,
    is_private BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES user(id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(id)
);

-- Create feedback table
CREATE TABLE IF NOT EXISTS feedback (
    id INT PRIMARY KEY AUTO_INCREMENT,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    rating INT,
    comment TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    is_anonymous BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (patient_id) REFERENCES user(id),
    FOREIGN KEY (doctor_id) REFERENCES doctor(id)
);

-- Create case_attachment table
CREATE TABLE IF NOT EXISTS case_attachment (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_id INT NOT NULL,
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INT NOT NULL,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    uploaded_by_id INT NOT NULL,
    FOREIGN KEY (case_id) REFERENCES `case`(id),
    FOREIGN KEY (uploaded_by_id) REFERENCES user(id)
);

-- Create case_transfer table
CREATE TABLE IF NOT EXISTS case_transfer (
    id INT PRIMARY KEY AUTO_INCREMENT,
    case_id INT NOT NULL,
    from_doctor_id INT NOT NULL,
    to_doctor_id INT NOT NULL,
    patient_id INT NOT NULL,
    transfer_reason TEXT,
    transfer_notes TEXT,
    patient_condition TEXT,
    patient_history TEXT,
    current_medications TEXT,
    transfer_priority VARCHAR(20),
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES `case`(id),
    FOREIGN KEY (from_doctor_id) REFERENCES doctor(id),
    FOREIGN KEY (to_doctor_id) REFERENCES doctor(id),
    FOREIGN KEY (patient_id) REFERENCES user(id)
); 