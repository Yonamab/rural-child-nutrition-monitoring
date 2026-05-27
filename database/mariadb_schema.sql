CREATE DATABASE IF NOT EXISTS nutrition_db;

USE nutrition_db;

CREATE TABLE IF NOT EXISTS villages (
    village_id VARCHAR(20) PRIMARY KEY,
    village_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS clinics (
    clinic_id VARCHAR(20) PRIMARY KEY,
    clinic_name VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS health_workers (
    health_worker_id VARCHAR(20) PRIMARY KEY,
    health_worker_name VARCHAR(100) NOT NULL,
    clinic_id VARCHAR(20),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id)
);

CREATE TABLE IF NOT EXISTS children (
    child_id VARCHAR(20) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    age_months INT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    village_id VARCHAR(20),
    FOREIGN KEY (village_id) REFERENCES villages(village_id)
);

CREATE TABLE IF NOT EXISTS measurements (
    measurement_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id VARCHAR(20),
    weight_kg DECIMAL(5,2),
    height_cm DECIMAL(5,2),
    muac_cm DECIMAL(5,2),
    feeding_frequency INT,
    symptoms TEXT,
    clinic_id VARCHAR(20),
    health_worker_id VARCHAR(20),
    measured_at DATETIME,
    FOREIGN KEY (child_id) REFERENCES children(child_id),
    FOREIGN KEY (clinic_id) REFERENCES clinics(clinic_id),
    FOREIGN KEY (health_worker_id) REFERENCES health_workers(health_worker_id)
);

CREATE TABLE IF NOT EXISTS alerts (
    alert_id INT AUTO_INCREMENT PRIMARY KEY,
    child_id VARCHAR(20),
    alert_type VARCHAR(100),
    alert_message TEXT,
    severity VARCHAR(50),
    created_at DATETIME,
    FOREIGN KEY (child_id) REFERENCES children(child_id)
);