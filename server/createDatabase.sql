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

CREATE TABLE stocks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    symbol VARCHAR(10),  
    company_name VARCHAR(100),
    sector VARCHAR(50),
    industry VARCHAR(50)
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

CREATE TABLE stockstransactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    stocksportfolios_id INT,
	FOREIGN KEY (stocksportfolios_id) REFERENCES stocksportfolios(id),
    transaction_type ENUM('buy', 'sell'),
    quantity INT DEFAULT 0,
    price DECIMAL(10, 2) DEFAULT 0.00,
    transaction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Step 1: Create an account for Giovanna
INSERT INTO accounts (balance) VALUES (0.00);

-- Step 2: Create user 'Giovanna' linked to the new account
INSERT INTO users (username, name, birth_date, email, account_id)
VALUES (
    'Giovanna',
    'Giovanna',
    '2000-11-06',
    'giovanna@example.com',
    LAST_INSERT_ID()
);

-- Step 3: Insert 5 tech stocks
INSERT INTO stocks (symbol, company_name, sector, industry) VALUES
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software'),
('GOOGL', 'Alphabet Inc.', 'Technology', 'Internet Services'),
('NVDA', 'NVIDIA Corporation', 'Technology', 'Semiconductors'),
('AMZN', 'Amazon.com, Inc.', 'Consumer Discretionary', 'E-Commerce');

-- Step 4: Create a portfolio for Giovanna’s account
INSERT INTO portfolios (account_id)
VALUES (
    (SELECT account_id FROM users WHERE username = 'Giovanna')
);

-- Step 5: Link all stocks to Giovanna’s portfolio
INSERT INTO stocksportfolios (portfolios_id, stock_id)
SELECT
    (SELECT id FROM portfolios WHERE account_id = (SELECT account_id FROM users WHERE username = 'Giovanna')),
    id
FROM stocks;

-- Step 6 (Optional): Set sample quantities and costs
UPDATE stocksportfolios
SET quantity = 10, average_cost = 150.00
WHERE stock_id = (SELECT id FROM stocks WHERE symbol = 'AAPL')
  AND portfolios_id = (SELECT id FROM portfolios WHERE account_id = (SELECT account_id FROM users WHERE username = 'Giovanna'));

UPDATE stocksportfolios
SET quantity = 5, average_cost = 3000.00
WHERE stock_id = (SELECT id FROM stocks WHERE symbol = 'GOOGL')
  AND portfolios_id = (SELECT id FROM portfolios WHERE account_id = (SELECT account_id FROM users WHERE username = 'Giovanna'));




--(b, tesouro selic), (b, cdb)
-- create table portofoliofixedincome (
--     portfolios_id INT FOREIGN KEY REFERENCES portfolios(id),
--     fixed_income_symbol VARCHAR(10) FOREIGN KEY REFERENCES fixedincome(symbol),
--     maturity_date DATE,
--     interest_rate DECIMAL(5, 2) DEFAULT 0.00,
--     price_paid DECIMAL(10, 2) DEFAULT 0.00,
--     UNIQUE (portfolios_id, fixed_income_symbol)
-- ); 










