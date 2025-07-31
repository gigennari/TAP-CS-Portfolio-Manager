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