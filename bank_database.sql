CREATE DATABASE IF NOT EXISTS bank;
USE bank;

CREATE TABLE bankaccount (
    bank_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_user VARCHAR(100) NOT NULL,
    bank_address VARCHAR(255) NOT NULL,
    bank_pin VARCHAR(4) NOT NULL,
    bank_balance DECIMAL(10,2) DEFAULT 0.00
);

CREATE TABLE transaction_logs (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    bank_id INT NOT NULL,
    action_type VARCHAR(50) NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    balance_after DECIMAL(10,2) NOT NULL,
    log_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (bank_id) REFERENCES bankaccount(bank_id) ON DELETE CASCADE
);