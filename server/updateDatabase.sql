-- 0. Clean the entire database
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE stockstransactions;
TRUNCATE TABLE stocksportfolios;
TRUNCATE TABLE stocks;
TRUNCATE TABLE portfolios;
TRUNCATE TABLE accounts;
TRUNCATE TABLE users;
SET FOREIGN_KEY_CHECKS = 1;

-- 1. Create a single user: Giovanna
INSERT INTO users (username, name, birth_date, email)
VALUES ('giovanna', 'Giovanna', '1990-01-01', 'giovanna@example.com');

-- 2. Create an account for Giovanna
INSERT INTO accounts (balance, user_id)
VALUES (20000.00, (SELECT id FROM users WHERE username='giovanna'));

-- 3. Create a portfolio for Giovanna
INSERT INTO portfolios (account_id, active)
VALUES ((SELECT id FROM accounts WHERE user_id=(SELECT id FROM users WHERE username='giovanna')), TRUE);

-- 4. Insert the stocks (AAPL and TSLA)
INSERT INTO stocks (symbol, company_name, sector, industry)
VALUES 
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
('TSLA', 'Tesla Inc.', 'Consumer Cyclical', 'Auto Manufacturers');

-- 5. Create stocksportfolio entries with initial quantity 0
INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost)
SELECT p.id, s.id, 0, 0
FROM portfolios p
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
JOIN stocks s ON s.symbol IN ('AAPL','TSLA')
WHERE u.username = 'giovanna';

-- 6. Insert transactions

-- Buy 10 AAPL on 2025-07-28
INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
SELECT sp.id, 'buy', 10, 200.00, '2025-07-28 10:00:00'
FROM stocksportfolios sp
JOIN stocks s ON sp.stock_id = s.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
WHERE u.username = 'giovanna' AND s.symbol = 'AAPL';

-- Buy 10 TSLA on 2025-07-28
INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
SELECT sp.id, 'buy', 10, 700.00, '2025-07-28 10:00:00'
FROM stocksportfolios sp
JOIN stocks s ON sp.stock_id = s.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
WHERE u.username = 'giovanna' AND s.symbol = 'TSLA';

-- Sell 5 AAPL on 2025-08-01
INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
SELECT sp.id, 'sell', 5, 210.00, '2025-08-01 10:00:00'
FROM stocksportfolios sp
JOIN stocks s ON sp.stock_id = s.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
WHERE u.username = 'giovanna' AND s.symbol = 'AAPL';

-- 7. Update quantities in stocksportfolios
-- AAPL final: 10 bought - 5 sold = 5
UPDATE stocksportfolios sp
JOIN stocks s ON sp.stock_id = s.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
SET sp.quantity = 5
WHERE u.username = 'giovanna' AND s.symbol = 'AAPL';

-- TSLA final: 10 bought
UPDATE stocksportfolios sp
JOIN stocks s ON sp.stock_id = s.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
SET sp.quantity = 10
WHERE u.username = 'giovanna' AND s.symbol = 'TSLA';
