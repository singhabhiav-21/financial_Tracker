


CREATE TABLE IF NOT EXISTS users(
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name    VARCHAR(50) NOT NULL ,
    email   VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_photo VARCHAR(255) NUll,
    date_added DATETIME DEFAULT current_timestamp
);

CREATE TABLE IF NOT EXISTS account(
    account_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    account_name VARCHAR(50) NOT NULL,
    account_type VARCHAR(50) NOT NULL,
    account_balance DECIMAL(12,2),
    currency VARCHAR(10) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    foreign key (user_id) references users(user_id)
);


CREATE TABLE IF NOT EXISTS category(
    category_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    name VARCHAR(50) NOT NULL,
    type VARCHAR (50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_on DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS transactions(
    transaction_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    category_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    amount DECIMAL(12,2) NOT NULL,
    description VARCHAR(255),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    transaction_date DATE,
    balance decimal(15,2),
    transaction_hash VARCHAR(250) NULL,
    FOREIGN KEY (user_id) references users(user_id),
    FOREIGN KEY (category_id) references category(category_id)
);



CREATE TABLE IF NOT EXISTS budget(
    budget_id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    category_id INT NULL,
    month INT NOT NULL CHECK ( month BETWEEN 1 AND 12),
    year INT NOT NULL,
    amount DECIMAL(10,2) NOT NULL CHECK(amount >= 0),
    FOREIGN KEY (user_id) references users(user_id),
    FOREIGN KEY (category_id) references  category(category_id)
);

CREATE TABLE IF NOT EXISTS reports
(
    report_id         INT PRIMARY KEY AUTO_INCREMENT,
    user_id           INT        NOT NULL,
    report_month      VARCHAR(7) NOT NULL,
    total_spending    DECIMAL(15, 2) DEFAULT 0,
    transaction_count INT            DEFAULT 0,
    generated_at      TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_month (user_id, report_month),
    INDEX idx_user_date (user_id, generated_at DESC)
);



