-- Schema for Use Case 5: Admin Creates Disaster Event
CREATE TABLE Admin (
    admin_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE DisasterEvent (
    event_id INT AUTO_INCREMENT PRIMARY KEY,
    event_name VARCHAR(100) NOT NULL,
    disaster_type ENUM('Hurricane', 'Earthquake', 'Flood', 'Fire', 'Tornado', 'Other') NOT NULL,
    location VARCHAR(255) NOT NULL,
    start_date DATE NOT NULL,
    end_date DATE,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES Admin(admin_id)
);

-- Schema for Use Case 6: Admin Manages Donation Categories and Items
CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE Item (
    item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    quantity INT DEFAULT 0,
    expiration_date DATE,
    category_id INT,
    created_by INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (created_by) REFERENCES Admin(admin_id)
);

-- Associative Table: Many-to-Many between DisasterEvent and Category
CREATE TABLE EventCategory (
    event_id INT,
    category_id INT,
    PRIMARY KEY (event_id, category_id),
    FOREIGN KEY (event_id) REFERENCES DisasterEvent(event_id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES Category(category_id) ON DELETE CASCADE
);
