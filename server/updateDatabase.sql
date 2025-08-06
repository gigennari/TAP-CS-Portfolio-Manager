-- 0. Clean the entire database
SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE stockstransactions;
TRUNCATE TABLE stocksportfolios;
TRUNCATE TABLE stocks;
TRUNCATE TABLE portfolios;
TRUNCATE TABLE accounts;
TRUNCATE TABLE users;
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

