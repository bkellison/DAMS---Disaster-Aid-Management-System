CREATE TABLE User (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE,
    role ENUM('Admin', 'Donor', 'Recipient', 'CallCenterOperator') NOT NULL,
    zip_code VARCHAR(10),
    is_active BOOLEAN DEFAULT TRUE
);

CREATE TABLE LoginAttempts (
    attempt_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT,
    attempt_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),
    status ENUM('Success', 'Failure') NOT NULL,
    device_info TEXT,
    failed_reason TEXT,
    FOREIGN KEY (user_id) REFERENCES User(user_id) ON DELETE CASCADE
);
