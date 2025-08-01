USE bygdb;

-- 1. Insert users
INSERT INTO users (username, name, birth_date, email)
VALUES 
('giovanna_g', 'Giovanna Gennari', '1998-03-11', 'giovanna@example.com'),
('john_doe', 'John Doe', '1990-07-15', 'john@example.com'),
('jane_smith', 'Jane Smith', '1985-12-02', 'jane@example.com');

-- 2. Create accounts for each user
INSERT INTO accounts (balance, user_id)
VALUES
(15000.00, 1),  -- Giovanna
(20000.00, 2),  -- John
(5000.00,  3);  -- Jane

-- 3. Create portfolios for each account
INSERT INTO portfolios (account_id, active)
VALUES
(1, TRUE), -- Giovanna
(2, TRUE), -- John
(3, TRUE); -- Jane

-- 4. Insert example stocks
INSERT INTO stocks (symbol, company_name, sector, industry)
VALUES 
('AAPL', 'Apple Inc.', 'Technology', 'Consumer Electronics'),
('MSFT', 'Microsoft Corporation', 'Technology', 'Software—Infrastructure'),
('TSLA', 'Tesla, Inc.', 'Consumer Cyclical', 'Auto Manufacturers'),
('AMZN', 'Amazon.com, Inc.', 'Consumer Cyclical', 'Internet Retail'),
('GOOGL', 'Alphabet Inc.', 'Communication Services', 'Internet Content & Information');

-- 5. Assign stocks to portfolios (mock holdings)
INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost)
VALUES
-- Giovanna's portfolio (id=1)
(1, 1, 10, 175.50), -- 10 AAPL
(1, 3, 2, 720.00),  -- 2 TSLA

-- John's portfolio (id=2)
(2, 2, 5, 320.00),  -- 5 MSFT
(2, 4, 1, 3300.00), -- 1 AMZN

-- Jane's portfolio (id=3)
(3, 5, 3, 2800.00); -- 3 GOOGL

-- 6. Record stock transactions
INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price)
VALUES
-- Giovanna's transactions
(1, 'buy', 10, 175.50),
(1, 'buy', 2, 720.00),
(1, 'sell', 5, 190.00),

-- John's transactions
(2, 'buy', 5, 320.00),
(2, 'buy', 1, 3300.00),

-- Jane's transactions
(3, 'buy', 3, 2800.00);
