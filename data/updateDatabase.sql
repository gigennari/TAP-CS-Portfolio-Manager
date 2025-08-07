USE bygdb;

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Truncate in reverse dependency order
TRUNCATE TABLE stockstransactions;
TRUNCATE TABLE stocksportfolios;
TRUNCATE TABLE portfolios;
TRUNCATE TABLE accounts;
TRUNCATE TABLE stocks;
TRUNCATE TABLE users;

-- Re-enable foreign key checks
SET FOREIGN_KEY_CHECKS = 1;


-- 1. Create users
INSERT INTO users (username, name, birth_date, email)
VALUES ('giovanna', 'Giovanna', '1990-01-01', 'giovanna@example.com');
INSERT INTO users (username, name, birth_date, email)
VALUES ('baibhav', 'Baibhav', '1990-01-01', 'baibhav@example.com');
INSERT INTO users (username, name, birth_date, email)
VALUES ('yixuan', 'Yixuan', '1990-01-01', 'yixuan@example.com');

-- 2. Create an account for users
INSERT INTO accounts (balance, user_id)
VALUES (25000.00, (SELECT id FROM users WHERE username='giovanna'));
INSERT INTO accounts (balance, user_id)
VALUES (25000.00, (SELECT id FROM users WHERE username='baibhav'));
INSERT INTO accounts (balance, user_id)
VALUES (25000.00, (SELECT id FROM users WHERE username='yixuan'));

-- 3. Create a portfolio for users
INSERT INTO portfolios (account_id, active)
VALUES ((SELECT id FROM accounts WHERE user_id=(SELECT id FROM users WHERE username='giovanna')), TRUE);
INSERT INTO portfolios (account_id, active)
VALUES ((SELECT id FROM accounts WHERE user_id=(SELECT id FROM users WHERE username='baibhav')), TRUE);
INSERT INTO portfolios (account_id, active)
VALUES ((SELECT id FROM accounts WHERE user_id=(SELECT id FROM users WHERE username='yixuan')), TRUE);

USE bygdb;

-- 1. Insert Disney, MSFT, TSLA into stocks if they don't exist
INSERT IGNORE INTO stocks (symbol, company_name, sector, industry)
VALUES 
('DIS', 'Walt Disney Co', 'Communication Services', 'Entertainment'),
('MSFT', 'Microsoft Corp', 'Technology', 'Software'),
('TSLA', 'Tesla Inc', 'Consumer Cyclical', 'Automotive');

-- --- Actual Prices ---
SET @price_dis_buy = 120.00;
SET @price_dis_sell = 121.00;
SET @price_msft = 513.00;
SET @price_tsla_buy = 315.00;
SET @price_tsla_sell = 309.00;

-- 2. Buy 10 Disney on 2025-07-25
INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost)
VALUES (1, (SELECT id FROM stocks WHERE symbol='DIS'), 10, @price_dis_buy)
ON DUPLICATE KEY UPDATE
    average_cost = ((average_cost * quantity) + (@price_dis_buy * 10)) / (quantity + 10),
    quantity = quantity + 10;

INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
VALUES (
    (SELECT id FROM stocksportfolios WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='DIS')),
    'buy', 10, @price_dis_buy, '2025-07-25'
);

UPDATE accounts 
SET balance = balance - (10 * @price_dis_buy)
WHERE id = (SELECT account_id FROM portfolios WHERE id = 1);

-- 3. Buy 10 MSFT on 2025-07-26
INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost)
VALUES (1, (SELECT id FROM stocks WHERE symbol='MSFT'), 10, @price_msft)
ON DUPLICATE KEY UPDATE
    average_cost = ((average_cost * quantity) + (@price_msft * 10)) / (quantity + 10),
    quantity = quantity + 10;

INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
VALUES (
    (SELECT id FROM stocksportfolios WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='MSFT')),
    'buy', 10, @price_msft, '2025-07-26'
);

UPDATE accounts 
SET balance = balance - (10 * @price_msft)
WHERE id = (SELECT account_id FROM portfolios WHERE id = 1);

-- 4. Buy 2 TSLA on 2025-07-26
INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost)
VALUES (1, (SELECT id FROM stocks WHERE symbol='TSLA'), 2, @price_tsla_buy)
ON DUPLICATE KEY UPDATE
    average_cost = ((average_cost * quantity) + (@price_tsla_buy * 2)) / (quantity + 2),
    quantity = quantity + 2;

INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
VALUES (
    (SELECT id FROM stocksportfolios WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='TSLA')),
    'buy', 2, @price_tsla_buy, '2025-07-26'
);

UPDATE accounts 
SET balance = balance - (2 * @price_tsla_buy)
WHERE id = (SELECT account_id FROM portfolios WHERE id = 1);

-- 5. Sell 5 Disney on 2025-07-28
UPDATE stocksportfolios
SET quantity = quantity - 5
WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='DIS');

INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
VALUES (
    (SELECT id FROM stocksportfolios WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='DIS')),
    'sell', 5, @price_dis_sell, '2025-07-28'
);

UPDATE accounts 
SET balance = balance + (5 * @price_dis_sell)
WHERE id = (SELECT account_id FROM portfolios WHERE id = 1);

-- 6. Sell 1 TSLA on 2025-08-01
UPDATE stocksportfolios
SET quantity = quantity - 1
WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='TSLA');

INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
VALUES (
    (SELECT id FROM stocksportfolios WHERE portfolios_id=1 AND stock_id=(SELECT id FROM stocks WHERE symbol='TSLA')),
    'sell', 1, @price_tsla_sell, '2025-08-01'
);

UPDATE accounts 
SET balance = balance + (1 * @price_tsla_sell)
WHERE id = (SELECT account_id FROM portfolios WHERE id = 1);
