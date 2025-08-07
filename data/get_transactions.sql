SELECT s.symbol, t.transaction_type, t.quantity, t.transaction_date
FROM stockstransactions t
JOIN stocksportfolios sp ON t.stocksportfolios_id = sp.id
JOIN portfolios p ON sp.portfolios_id = p.id
JOIN accounts a ON p.account_id = a.id
JOIN users u ON a.user_id = u.id
JOIN stocks s ON sp.stock_id = s.id
WHERE u.id = 1
AND t.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
ORDER BY t.transaction_date