CREATE DATABASE bygDB;

USE bygDB;

CREATE TABLE accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    balance DECIMAL(10, 2) DEFAULT 0.00
);

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    name VARCHAR(100),
    birth_date DATE,
    email VARCHAR(100) UNIQUE,
    account_id INT,
	FOREIGN KEY (account_id)  REFERENCES accounts(id)
    );

CREATE TABLE  portfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    account_id INT,
	FOREIGN KEY (account_id) REFERENCES accounts(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    active BOOLEAN DEFAULT TRUE
);

CREATE TABLE stocksportfolios (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolios_id INT, 
    FOREIGN KEY (portfolios_id) REFERENCES portfolios(id),
    stock_id INT,
    FOREIGN KEY (stock_id) REFERENCES stocks(id),
    quantity INT DEFAULT 0,
    average_cost DECIMAL(10, 2) DEFAULT 0.00,
    UNIQUE (portfolios_id, stock_id)
);

CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),  
    company_name VARCHAR(100),
    sector VARCHAR(50),
    industry VARCHAR(50)
    );

CREATE TABLE stockstransactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stocksportfolios_id INT,
	FOREIGN KEY (stocksportfolios_id) REFERENCES stocksportfolios(id),
    transaction_type ENUM('buy', 'sell'),
    quantity INT DEFAULT 0,
    price DECIMAL(10, 2) DEFAULT 0.00,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



--(b, tesouro selic), (b, cdb)
-- create table portofoliofixedincome (
--     portfolios_id INT FOREIGN KEY REFERENCES portfolios(id),
--     fixed_income_symbol VARCHAR(10) FOREIGN KEY REFERENCES fixedincome(symbol),
--     maturity_date DATE,
--     interest_rate DECIMAL(5, 2) DEFAULT 0.00,
--     price_paid DECIMAL(10, 2) DEFAULT 0.00,
--     UNIQUE (portfolios_id, fixed_income_symbol)
-- ); 










