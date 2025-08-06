from flask import Blueprint, request, jsonify
import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from db import init_db, dump_db
from time import sleep
import pandas as pd
from decimal import Decimal
import feedparser
# import API keys from Python config
from config import CONFIG, RANDOM_STOCKS
import random

portfolio_bp = Blueprint('portfolio', __name__)

# API config from Python config file
ALPHA_VANTAGE_API_KEY = CONFIG.ALPHA_VANTAGE_API_KEY
ALPHA_VANTAGE_BASE_URL = CONFIG.ALPHA_VANTAGE_BASE_URL
FINNHUB_TOKEN = CONFIG.FINNHUB_API_TOKEN


#get all users from users table
@portfolio_bp.route('/users', methods=['GET'])
def get_users():
    """Get all users from the users table"""
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM users")
        
        users = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        return jsonify({"users": users})
        
    except Exception as e:
        print(f"Error getting users: {e}")
        return jsonify({"error": "Failed to get users"}), 500

#get portfolio balance (accounts table)
@portfolio_bp.route('/balance', methods=['GET'])
def get_balance():
    # Implementation for getting portfolio balance
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
           
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if result:
            return jsonify({"balance": result['balance']})
        else:
            return jsonify({"balance": 0.00})
            
    except Exception as e:
        print(f"Error getting balance: {e}")
        return jsonify({"error": "Failed to get balance"}), 500

#process transaction (buy/sell) -> REMOVE LIMIT ORDERS 
#----(request must have user id, qty, current price , stock symbol, type of operation)


@portfolio_bp.route('/portfoliovalue', methods=['GET'])
def get_total_portfolio_value():
    """Get total portfolio value for a user"""
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        cursor.execute("""
            SELECT SUM(sp.quantity * s.current_price) AS total_value
            FROM stocksportfolio sp
            JOIN stocks s ON sp.symbol = s.symbol
            WHERE sp.user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        total_value = result['total_value'] if result['total_value'] else 0.00
        
        return jsonify({"totalPortfolioValue": total_value})
        
    except Exception as e:
        print(f"Error getting total portfolio value: {e}")
        return jsonify({"error": "Failed to get total portfolio value"}), 500
    
    
@portfolio_bp.route('/wallet', methods=['GET'])
def get_wallet():
    """Get user's wallet/portfolio with current stock prices"""
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')
        
        if not user_id:
            return jsonify({"error": "user_id is required"}), 400
        
        # Get user's stock portfolio with symbol, quantity, avg_cost, company_name
        cursor.execute("""
            SELECT s.symbol, sp.quantity, sp.average_cost AS avg_cost, s.company_name
            FROM accounts a  
            INNER JOIN portfolios p ON a.id = p.account_id
            JOIN stocksportfolios sp ON p.id = sp.portfolios_id
            JOIN stocks s ON sp.stock_id = s.id
            WHERE a.user_id = %s AND sp.quantity > 0
            ORDER BY s.symbol;
        """, (user_id,))
        
        portfolio_stocks = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not portfolio_stocks:
            return jsonify({"wallet": [], "totalValue": 0.00})
        
        wallet_data = []
        total_portfolio_value = 0.00
        
        for stock in portfolio_stocks:
            symbol = stock['symbol']
            # print(symbol)
            quantity = float(stock['quantity'])
            avg_cost = float(stock['avg_cost']) if stock['avg_cost'] else 0.00
            name = stock.get('company_name', symbol)

            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="7d")

                current_price = float(hist['Close'].iloc[-1]) if not hist.empty else 0.00
                price_24h = float(hist['Close'].iloc[-2]) if len(hist) > 1 else current_price
                price_7d = float(hist['Close'].iloc[0]) if len(hist) > 0 else current_price

                change_1h = 0.00  # Yahoo doesn't support 1h granularity
                change_24h = ((current_price - price_24h) / price_24h * 100) if price_24h > 0 else 0.00
                change_7d = ((current_price - price_7d) / price_7d * 100) if price_7d > 0 else 0.00

                market_value = quantity * current_price
                total_cost = quantity * avg_cost
                gain_loss = market_value - total_cost
                gain_loss_percent = (gain_loss / total_cost * 100) if total_cost > 0 else 0.00

                # Use fast_info for limited info (faster than .info)
                info = ticker.fast_info if hasattr(ticker, "fast_info") else {}
                sector = ticker.info.get("sector", "Unknown")
                industry = ticker.info.get("industry", "Unknown")

                wallet_item = {
                    "symbol": symbol,
                    "name": name,
                    "quantity": quantity,
                    "avgCost": avg_cost,
                    "currentPrice": current_price,
                    "marketValue": market_value,
                    "gainLoss": gain_loss,
                    "gainLossPercent": gain_loss_percent,
                    "change1h": change_1h,
                    "change24h": change_24h,
                    "change7d": change_7d,
                    "marketCap": info.get("market_cap", 0),
                    "volume": info.get("volume", 0),
                    "sector": sector,
                    "industry": industry
                }

            except Exception as stock_error:
                print(f"Error processing stock {symbol}: {stock_error}")
                market_value = quantity * 0.00
                wallet_item = {
                    "symbol": symbol,
                    "name": name,
                    "quantity": quantity,
                    "avgCost": avg_cost,
                    "currentPrice": 0.00,
                    "marketValue": market_value,
                    "gainLoss": 0.00,
                    "gainLossPercent": 0.00,
                    "change1h": 0.00,
                    "change24h": 0.00,
                    "change7d": 0.00,
                    "marketCap": 0,
                    "volume": 0,
                    "sector": "Unknown",
                    "industry": "Unknown"
                }

            wallet_data.append(wallet_item)
            total_portfolio_value += wallet_item["marketValue"]
        
        return jsonify({
            "wallet": wallet_data,
            "totalValue": round(total_portfolio_value, 2),
            "count": len(wallet_data)
        })

    except Exception as e:
        print(f"Error getting wallet: {e}")
        return jsonify({"error": f"Failed to get wallet data: {str(e)}"}), 500





    
@portfolio_bp.route('/trade', methods=['POST'])
def execute_trade():
    """Execute a trade order"""
    try:
        data = request.get_json()
        print("data", data)
        
        required_fields = ['user_id', 'symbol', 'action', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = data['user_id']
        symbol = data['symbol'].upper()
        action = data['action'].lower()  # 'buy' or 'sell'
        quantity = Decimal(data['quantity'])
        order_type = data.get('orderType', 'market') # market or limit 
        price = Decimal(data.get('estimatedPrice', None))
        
        if action not in ['buy', 'sell']:
            return jsonify({"error": "Action must be 'buy' or 'sell'"}), 400
        
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400
        
        # Get current stock price for validation
        ticker = yf.Ticker(symbol)
        
        # Calculate trade value
        # send an erorr message for limit orders, sying it is not supported yet
        if order_type == 'limit':
            return jsonify({"error": "Limit price must be positive"}), 400
        
        if order_type == 'market':
            trade_price = price
            
        
            # Here you would typically:
            # 1. Check user's account balance (for buy orders)  
            date = datetime.now().isoformat()
            if action == 'buy':
                result = buy_stock(user_id, symbol, quantity, trade_price, date)
            # 2. Check user's stock holdings (for sell orders)
            elif action == 'sell':
                result = sell_stock(user_id, symbol, quantity, trade_price, date)
           
        
        
        # # For now, we'll simulate a successful trade
        # order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{symbol}"
        
        # trade_result = {
        #     "success": True,
        #     "orderId": order_id,
        #     "user_id": user_id,
        #     "symbol": symbol,
        #     "action": action,
        #     "quantity": quantity,
        #     "price": trade_price,
        #     "totalValue": trade_value,
        #     "orderType": order_type,
        #     "timestamp": datetime.now().isoformat(),
        #     "status": "executed"
        # }
        
        return result, 200
        
    except ValueError as e:
        return jsonify({"error": "Invalid quantity or price format"}), 400
    except Exception as e:
        print(f"Error executing trade: {e}")
        return jsonify({"error": "Failed to execute trade"}), 500

    
#buy stock -> update stocksportfolio qty and avg cost (include symbol if not there yet), update accounts balance, update stcoks table if we don't have the symbol there yet,  

#buy stock -> update stocksportfolio qty and avg cost (include symbol if not there yet), update accounts balance, update stcoks table if we don't have the symbol there yet,  
def buy_stock(user_id, symbol, quantity, price, date):
    # Implementation for buying stocks
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
        result = cursor.fetchone()
        balance = result['balance'] 
        
        
        #check if user has enough balance
        if balance > (quantity * price):
            
            # Deduct the amount from user's balance
            new_balance = balance - (quantity * price)
            print("new_balance", new_balance)
            cursor.execute("UPDATE accounts SET balance = %s WHERE user_id = %s", (new_balance, user_id))  
            conn.commit()

            #get portfolio id for user 
            cursor.execute("SELECT id FROM portfolios WHERE account_id = (SELECT id FROM accounts WHERE user_id = %s)", (user_id,)) #this will need to be changed if we have multiple portfolios per user
            portfolio_id = cursor.fetchone()['id']
            print("portfolio_id", portfolio_id)
        
            
            #check if stock exists in stocksportfolios for that given user
            cursor.execute("SELECT sp.id as row_num, sp.quantity, sp.average_cost, sp.stock_id, s.symbol FROM stocksportfolios sp JOIN accounts a on a.user_id = %s JOIN portfolios p on a.id = p.account_id JOIN stocks s on s.id = sp.stock_id AND s.symbol =%s", (user_id, symbol))
            stock = cursor.fetchone()
            row_num_on_stocksportfolio = stock['row_num'] if stock else None
            print("row_num_on_stocksportfolio", row_num_on_stocksportfolio)
            
            # update stocksportfolio table with new stock OR update stocksportfolios existing row with new stock quantity and avg cost
            #if it exists, update quantity and avg cost
            if stock:
                print("stock exists in stocksportfolio")
                #update stocksportfolio with new quantity and avg cost
                new_quantity = stock['quantity'] + quantity
                new_avg_cost = (stock['average_cost'] * stock['quantity'] + price * quantity) / new_quantity
                cursor.execute("UPDATE stocksportfolios SET quantity=%s, average_cost=%s WHERE id=%s", (new_quantity, new_avg_cost, row_num_on_stocksportfolio))
                conn.commit()
                                             
             #else, insert new stock into stocksportfolio
            else:
                print("stock does not exist in stocksportfolio")
                #check if stock exists in stocks table
                cursor.execute("SELECT id FROM stocks WHERE symbol = %s", (symbol,))
                stocks_exists = cursor.fetchone()
                
                if not stocks_exists:
                    print("stock does not exist in stocks table, inerting new stock")
                    #insert new stock into stocks table
                    insert_stock_in_stocks_table(symbol, cursor, conn)
                    #get stock id from stocks table
                
                cursor = conn.cursor(dictionary=True)
                cursor.execute("SELECT id FROM stocks WHERE symbol = %s", (symbol,))
                stock_data = cursor.fetchone()
                print("stock_data", stock_data)
                stock_id = stock_data['id'] 
                print("here is the stock_id", stock_id)
                         
                #insert new stock into stocksportfolio
                cursor.execute("INSERT INTO stocksportfolios (portfolios_id, stock_id, quantity, average_cost) VALUES (%s, %s, %s, %s)", (portfolio_id, stock_id, quantity, price))
                conn.commit()
                row_num_on_stocksportfolio = cursor.lastrowid
                print("row_num_on_stocksportfolio after insert", row_num_on_stocksportfolio)
                
            
            # insert transaction into stockstransactions table
            cursor.execute("INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date) VALUES (%s, %s, %s, %s, %s)", (row_num_on_stocksportfolio, 'buy', quantity, price, date))
            conn.commit()
            
            # Commit the transaction
            conn.commit()
            cursor.close()
            conn.close()
            
            return jsonify({"success": True, "message": "Stock purchased successfully"})
        
        else:
            # Insufficient balance
            cursor.close()
            conn.close()
            return jsonify({"error": "Insufficient balance for this purchase"}), 400

    except Exception as e:
        print(f"Error buying stock: {e}")
        return jsonify({"error": "Failed to buy stock"}), 500
    

    
#inserts a stocks intro the stock table 
def insert_stock_in_stocks_table(symbol, cursor, conn):
    #symbol, company_name, sector, industry
    
    ticker = yf.Ticker(symbol)
    company_name = ticker.info.get("longName", "Unknown")   
    sector = ticker.info.get("sector", "Unknown")
    industry = ticker.info.get("industry", "Unknown")
      
    cursor.execute("INSERT INTO stocks (symbol, company_name, sector, industry) VALUES (%s, %s, %s, %s)", (symbol, company_name, sector, industry))
    conn.commit()  
      
    

def sell_stock(user_id, symbol, quantity, current_price, date):
    """Sell stock for a user"""
    try:
        # Input validation
        if not user_id or not symbol or not quantity or not current_price:
            return {"success": False, "error": "Missing required parameters"}
        
        if quantity <= 0:
            return {"success": False, "error": "Quantity must be positive"}
        
        if current_price <= 0:
            return {"success": False, "error": "Price must be positive"}
        
        # Database connection
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        
        # Check if user has enough stock to sell
        # Join through the relationship chain: users -> accounts -> portfolios -> stocksportfolios -> stocks
        cursor.execute("""
            SELECT sp.id as stocksportfolio_id, sp.quantity, sp.average_cost, s.symbol, s.company_name
            FROM users u
            JOIN accounts a ON u.id = a.user_id
            JOIN portfolios p ON a.id = p.account_id
            JOIN stocksportfolios sp ON p.id = sp.portfolios_id
            JOIN stocks s ON sp.stock_id = s.id
            WHERE u.id = %s AND s.symbol = %s AND sp.quantity > 0
        """, (user_id, symbol.upper()))
        
        stock_holding = cursor.fetchone()
        
        # Check if user owns this stock
        if not stock_holding:
            cursor.close()
            conn.close()
            return {"success": False, "error": f"You don't own any shares of {symbol}"}
        
        # Check if user has enough shares to sell
        current_quantity = stock_holding['quantity']
        if current_quantity < quantity:
            cursor.close()
            conn.close()
            return {"success": False, "error": f"Insufficient shares. You own {current_quantity} shares but trying to sell {quantity}"}
        
        # Calculate remaining quantity and sale proceeds
        remaining_quantity = current_quantity - quantity
        sale_proceeds = quantity * current_price
        stocksportfolio_id = stock_holding['stocksportfolio_id']
        
        # Start transaction for database updates
        try:
            # 1. Insert transaction record into stockstransactions table
            cursor.execute("""
                INSERT INTO stockstransactions (stocksportfolios_id, transaction_type, quantity, price, transaction_date)
                VALUES (%s, 'sell', %s, %s, NOW())
            """, (stocksportfolio_id, quantity, current_price))
            conn.commit()
                

                # Update quantity if shares remain
            cursor.execute("""
                UPDATE stocksportfolios 
                SET quantity = %s 
                WHERE id = %s
            """, (remaining_quantity, stocksportfolio_id))
            conn.commit()

            # 3. Update user's account balance (add sale proceeds)
            cursor.execute("""
                UPDATE accounts a
                JOIN portfolios p ON a.id = p.account_id
                JOIN stocksportfolios sp ON p.id = sp.portfolios_id
                SET a.balance = a.balance + %s
                WHERE sp.id = %s
            """, (sale_proceeds, stocksportfolio_id))

            conn.commit()
            
            cursor.close()
            conn.close()
            
            # Return success with transaction details
            return {
                "success": True,
                "message": f"Successfully sold {quantity} shares of {symbol} for ${sale_proceeds:.2f}",
                "transaction_details": {
                    "symbol": symbol,
                    "quantity_sold": quantity,
                    "price_per_share": current_price,
                    "total_proceeds": sale_proceeds,
                    "remaining_shares": remaining_quantity,
                    "shares_deleted": remaining_quantity == 0
                }
            }
            
        except Exception as db_error:
            # Rollback transaction on error
            conn.rollback()
            cursor.close()
            conn.close()
            print(f"Database transaction error: {db_error}")
            return {"success": False, "error": f"Failed to complete sell transaction: {str(db_error)}"}
        
    except Exception as e:
        print(f"Error in sell_stock validation: {e}")
        return {"success": False, "error": f"Database error: {str(e)}"}


#alpha vatnage search utility function to search stocks 
@portfolio_bp.route('/search', methods=['GET'])
def search_stocks():
    """Search for stocks using Alpha Vantage API"""
    query = request.args.get('query', '').strip()
    
    if not query or len(query) < 2:
        return jsonify({"error": "Query must be at least 2 characters"}), 400
    
    try:
        # Alpha Vantage Symbol Search
        params = {
            'function': 'SYMBOL_SEARCH',
            'keywords': query,
            'apikey': ALPHA_VANTAGE_API_KEY
        }
        
        response = requests.get(ALPHA_VANTAGE_BASE_URL, params=params)
        data = response.json()
        
        if 'bestMatches' in data:
            results = []
            for match in data['bestMatches'][:10]:  # Limit to 10 results
                results.append({
                    'symbol': match.get('1. symbol', ''),
                    'name': match.get('2. name', ''),
                    'type': match.get('3. type', ''),
                    'region': match.get('4. region', ''),
                    'currency': match.get('8. currency', '')
                })
            return jsonify({"results": results})
        else:
            return jsonify({"results": []})
            
    except Exception as e:
        print(f"Error searching stocks: {e}")
        return jsonify({"error": "Failed to search stocks"}), 500


#get stock info with yahoo finance API - NOT WORKING - NEEDS TO BE FIXED 
@portfolio_bp.route('/stock/<symbol>', methods=['GET'])
def get_stock_info(symbol):
    """Get detailed stock information using Yahoo Finance"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        # Get current price and basic info
        stock_data = {
            'symbol': symbol.upper(),
            'name': info.get('longName', info.get('shortName', symbol)),
            'currentPrice': info.get('currentPrice', info.get('regularMarketPrice', 0)),
            'previousClose': info.get('previousClose', 0),
            'marketCap': info.get('marketCap', 0),
            'volume': info.get('volume', 0),
            'averageVolume': info.get('averageVolume', 0),
            'peRatio': info.get('trailingPE', 0),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'fiftyTwoWeekHigh': info.get('fiftyTwoWeekHigh', 0),
            'fiftyTwoWeekLow': info.get('fiftyTwoWeekLow', 0),
            'dividendYield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'eps': info.get('trailingEps', 0),
            'bookValue': info.get('bookValue', 0),
            'priceToBook': info.get('priceToBook', 0),
            'currency': info.get('currency', 'USD')
        }
        
        # Calculate change and change percent
        if stock_data['currentPrice'] and stock_data['previousClose']:
            change = stock_data['currentPrice'] - stock_data['previousClose']
            change_percent = (change / stock_data['previousClose']) * 100
            stock_data['change'] = change
            stock_data['changePercent'] = change_percent
        else:
            stock_data['change'] = 0
            stock_data['changePercent'] = 0
        
        # Convert dividend yield to percentage
        if stock_data['dividendYield']:
            stock_data['dividendYield'] = stock_data['dividendYield'] * 100
        
        return jsonify(stock_data)
        
    except Exception as e:
        print(f"Error getting stock info for {symbol}: {e}")
        return jsonify({"error": f"Failed to get stock information for {symbol}"}), 500



@portfolio_bp.route('/stock/<symbol>/history', methods=['GET'])
def get_stock_history(symbol):
    """Get historical stock data for charting"""
    try:
        period = request.args.get('period', '1d')  # 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max
        interval = request.args.get('interval', '1m')  # 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
        
        # Map frontend periods to yfinance periods
        period_mapping = {
            '1D': {'period': '1d', 'interval': '5m'},
            '5D': {'period': '5d', 'interval': '15m'},
            '1M': {'period': '1mo', 'interval': '1d'},
            '3M': {'period': '3mo', 'interval': '1d'},
            '1Y': {'period': '1y', 'interval': '1d'}
        }
        
        frontend_period = request.args.get('frontend_period', '1D')
        if frontend_period in period_mapping:
            period = period_mapping[frontend_period]['period']
            interval = period_mapping[frontend_period]['interval']
        
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period, interval=interval)
        
        if hist.empty:
            return jsonify({"error": "No historical data found"}), 404
        
        # Convert to format suitable for Chart.js
        chart_data = {
            'labels': [],
            'data': []
        }
        
        for index, row in hist.iterrows():
            # Format timestamp based on interval
            if interval in ['1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h']:
                label = index.strftime('%H:%M')
            else:
                label = index.strftime('%m/%d')
            
            chart_data['labels'].append(label)
            chart_data['data'].append(float(row['Close']))
        
        return jsonify(chart_data)
        
    except Exception as e:
        print(f"Error getting stock history for {symbol}: {e}")
        return jsonify({"error": f"Failed to get stock history for {symbol}"}), 500
    
    
@portfolio_bp.route('/historical-data', methods=['GET'])
def get_historical_data_for_user():
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Fetch user's stock transactions
        query = """
            SELECT s.symbol, t.transaction_type, t.quantity, t.transaction_date
            FROM stockstransactions t
            JOIN stocksportfolios sp ON t.stocksportfolios_id = sp.id
            JOIN portfolios p ON sp.portfolios_id = p.id
            JOIN accounts a ON p.account_id = a.id
            JOIN users u ON a.user_id = u.id
            JOIN stocks s ON sp.stock_id = s.id
            WHERE u.id = %s
            AND t.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            ORDER BY t.transaction_date;
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify([])

        df = pd.DataFrame(rows)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['date'] = df['transaction_date'].dt.date
        df['signed_qty'] = df.apply(lambda x: x['quantity'] if x['transaction_type'] == 'buy' else -x['quantity'], axis=1)

        # Aggregate daily position per symbol
        daily_positions = (
            df.groupby(['date', 'symbol'])['signed_qty'].sum()
            .groupby(level=1).cumsum().reset_index()
        )
        daily_positions.rename(columns={'signed_qty': 'shares'}, inplace=True)

        # Date range
        start_date = datetime.today().date() - timedelta(days=365)
        end_date = datetime.today().date()
        date_range = pd.date_range(start=start_date, end=end_date)
        portfolio_values = pd.DataFrame(index=date_range)

        # print("portfolio_values:", portfolio_values)
        # print("daily positions:", daily_positions)
        # Loop through each symbol
        for symbol in daily_positions['symbol'].unique():
            hist = yf.download(symbol, start=start_date, end=end_date, auto_adjust=True)['Close']
            hist.index = hist.index.date
            # print("hist:", hist)

            symbol_positions = (
                daily_positions[daily_positions['symbol'] == symbol]
                .set_index('date')
                .reindex(date_range.date, method='ffill')
                .fillna(0)
            )
            
            # print("symbol_positions:", symbol_positions)
            
            shares = symbol_positions['shares'].reindex(date_range.date, fill_value=0).ffill()
            # print("shares:",shares)
            # print(type(shares))
            prices = hist.reindex(date_range.date).ffill()
            # print("prices:",prices)
            # print(type(prices))
            # print(type(portfolio_values))
            
            df_test = shares * prices[symbol]
            # print("df_test:", df_test)
            # print(type(df_test))

            portfolio_values[symbol] = shares * prices[symbol]
            # print(portfolio_values[symbol])

        # print("portfolio_values:", portfolio_values)
        portfolio_values['total_value'] = portfolio_values.sum(axis=1)
        result = (
            portfolio_values['total_value']
            .reset_index()
            .rename(columns={'index': 'date', 'total_value': 'value'})
            .to_dict(orient='records')
        )

        return jsonify(result)

    except Exception as e:
        print(f"Error getting historical data: {e}")
        return jsonify({"error": f"Failed to get historical data: {e}"}), 500

        
@portfolio_bp.route('/historical-cost', methods=['GET'])
def get_historical_cost_for_user():
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        query = """
            SELECT t.transaction_type, t.quantity, t.price, t.transaction_date
            FROM stockstransactions t
            JOIN stocksportfolios sp ON t.stocksportfolios_id = sp.id
            JOIN portfolios p ON sp.portfolios_id = p.id
            JOIN accounts a ON p.account_id = a.id
            JOIN users u ON a.user_id = u.id
            WHERE u.id = %s
              AND t.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            ORDER BY t.transaction_date;
        """
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        if not rows:
            return jsonify([])

        df = pd.DataFrame(rows)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['date'] = df['transaction_date'].dt.date

        # Compute signed cost per transaction
        df['signed_cost'] = df.apply(
            lambda x: x['quantity'] * float(x['price']) if x['transaction_type'] == 'buy' else -x['quantity'] * float(x['price']),
            axis=1
        )

        # Aggregate signed cost by day
        daily_cost = df.groupby('date')['signed_cost'].sum()

        # Generate full date range
        start_date = datetime.today().date() - timedelta(days=365)
        end_date = datetime.today().date()
        date_range = pd.date_range(start=start_date, end=end_date)
        cost_df = pd.DataFrame(index=date_range)
        cost_df.index.name = 'date'

        # Fill missing dates and compute cumulative spend
        cost_df['daily_cost'] = daily_cost.reindex(date_range.date, fill_value=0)
        cost_df['total_cost'] = cost_df['daily_cost'].cumsum()

        result = (
            cost_df['total_cost']
            .reset_index()
            .rename(columns={'total_cost': 'value'})
            .to_dict(orient='records')
        )

        return jsonify(result)

    except Exception as e:
        print(f"Error getting historical cost: {e}")
        return jsonify({"error": f"Failed to get historical cost: {e}"}), 500

def get_user_stocks(user_id):
    """Fetch up to 10 stocks from DB, fill with random if less than 10."""
    conn = init_db()
    cursor = conn.cursor(dictionary=True)
    
    
    cursor.execute("""
        SELECT DISTINCT stock_id, stocks.symbol AS symbol
        FROM stocksportfolios
        JOIN stocks ON stocksportfolios.stock_id = stocks.id
        WHERE portfolios_id = %s
        LIMIT 10
    """, (user_id,))
    rows = cursor.fetchall()
    conn.close()

    stocks = [row['symbol'] for row in rows]
    print(stocks)
    # Fill to 10 with random fallback symbols
    while len(stocks) < 10:
        extra = random.choice(RANDOM_STOCKS)
        if extra not in stocks:
            stocks.append(extra)
    return stocks

def get_finnhub_data(symbol):
    """Fetch recommendation, price-target, and sentiment for a symbol using Finnhub."""
    
    # Get company name using Yahoo Finance (same as get_stock_info)
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        company_name = info.get('longName', info.get('shortName', symbol))
    except Exception as e:
        print(f"Error getting company name for {symbol}: {e}")
        company_name = symbol
    
    # Analyst Recommendations
    rec_url = f"https://finnhub.io/api/v1/stock/recommendation?symbol={symbol}&token={FINNHUB_TOKEN}"
    rec_data = requests.get(rec_url).json()
    recommendation = rec_data[0] if rec_data else {}

    # Price Targets
    target_url = f"https://finnhub.io/api/v1/stock/price-target?symbol={symbol}&token={FINNHUB_TOKEN}"
    price_target = requests.get(target_url).json()

    # News Sentiment
    sentiment_url = f"https://finnhub.io/api/v1/news-sentiment?symbol={symbol}&token={FINNHUB_TOKEN}"
    sentiment = requests.get(sentiment_url).json()

    return {
        "symbol": symbol,
        "company_name": company_name,
        "recommendations": {
            "strongBuy": recommendation.get("strongBuy", 0),
            "buy": recommendation.get("buy", 0),
            "hold": recommendation.get("hold", 0),
            "sell": recommendation.get("sell", 0),
            "strongSell": recommendation.get("strongSell", 0)
        },
        "price_targets": {
            "low": price_target.get("targetLow"),
            "average": price_target.get("targetMean"),
            "high": price_target.get("targetHigh")
        },
        "sentiment": {
            "bullishPercent": sentiment.get("bullishPercent", 0),
            "bearishPercent": sentiment.get("bearishPercent", 0),
            "companyNewsScore": sentiment.get("companyNewsScore", 0)
        }
    }
    
@portfolio_bp.route('/historical-balance', methods=['GET'])
def get_historical_balance_for_user():
    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Get current account balance
        cursor.execute("""
            SELECT a.balance 
            FROM accounts a
            WHERE a.user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Account not found"}), 404

        current_balance = result['balance']

        # Get all transactions in the past year
        query = """
            SELECT t.transaction_type, t.price, t.quantity, t.transaction_date
            FROM stockstransactions t
            JOIN stocksportfolios sp ON t.stocksportfolios_id = sp.id
            JOIN portfolios p ON sp.portfolios_id = p.id
            JOIN accounts a ON p.account_id = a.id
            WHERE a.user_id = %s
            AND t.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            ORDER BY t.transaction_date DESC
        """
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['date'] = df['transaction_date'].dt.date

        # Cash flow REVERSED to undo effects day by day
        df['reverse_cash'] = df.apply(
            lambda x: x['price'] * x['quantity'] if x['transaction_type'] == 'buy' else -x['price'] * x['quantity'],
            axis=1
        )

        # Aggregate by day
        daily_reversal = df.groupby('date')['reverse_cash'].sum()

        # Build full date range
        end_date = datetime.today().date()
        start_date = end_date - timedelta(days=365)
        date_range = pd.date_range(start=start_date, end=end_date)
        balance_series = pd.Series(
            [Decimal('0.00')] * len(date_range),
            index=date_range.date,
            dtype='object'
        )
        balance_series[:] = 0

        # Fill in reversed cash changes
        balance_series.update(daily_reversal)

        # Backward cumulative sum (from today → past), then reverse it
        balance_series = balance_series[::-1].cumsum()[::-1]

        # Add current balance to get historical balances
        balance_series = current_balance + balance_series

        result = [{'date': str(date), 'balance': round(balance, 2)} for date, balance in balance_series.items()]
        return jsonify(result)

    except Exception as e:
        print(f"Error getting historical balance: {e}")
        return jsonify({"error": f"Failed to get historical balance: {e}"}), 500

    try:
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        user_id = request.args.get('user_id')

        if not user_id:
            return jsonify({"error": "user_id is required"}), 400

        # Get user's initial account balance
        cursor.execute("""
            SELECT a.balance 
            FROM accounts a
            WHERE a.user_id = %s
        """, (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({"error": "Account not found"}), 404

        initial_balance = result['balance']

        # Fetch user's transactions from past year
        query = """
            SELECT t.transaction_type, t.price, t.quantity, t.transaction_date
            FROM stockstransactions t
            JOIN stocksportfolios sp ON t.stocksportfolios_id = sp.id
            JOIN portfolios p ON sp.portfolios_id = p.id
            JOIN accounts a ON p.account_id = a.id
            WHERE a.user_id = %s
            AND t.transaction_date >= DATE_SUB(CURDATE(), INTERVAL 1 YEAR)
            ORDER BY t.transaction_date;
        """
        cursor.execute(query, (user_id,))
        transactions = cursor.fetchall()

        cursor.close()
        conn.close()

        # Convert to DataFrame
        df = pd.DataFrame(transactions)
        if df.empty:
            # No transactions, balance remains unchanged
            date_range = pd.date_range(end=datetime.today(), periods=365)
            result = [{'date': d.date().isoformat(), 'balance': round(initial_balance, 2)} for d in date_range]
            return jsonify(result)

        df['transaction_date'] = pd.to_datetime(df['transaction_date'])
        df['date'] = df['transaction_date'].dt.date

        # Compute cash movement per transaction
        df['cash_flow'] = df.apply(
            lambda x: -x['price'] * x['quantity'] if x['transaction_type'] == 'buy' else x['price'] * x['quantity'],
            axis=1
        )

        # Aggregate daily net cash movement
        daily_cash = df.groupby('date')['cash_flow'].sum()

        # Prepare full date range
        start_date = datetime.today().date() - timedelta(days=365)
        end_date = datetime.today().date()
        date_range = pd.date_range(start=start_date, end=end_date)
        balance_series = pd.Series(index=date_range.date, dtype='float64')

        # Fill with daily net cash movement, NaN elsewhere
        balance_series.update(daily_cash)

        # Replace NaNs with 0 and compute cumulative sum
        balance_series = balance_series.fillna(0).cumsum()

        # Add initial balance
        balance_series = initial_balance + balance_series

        # Format output
        result = [{'date': str(date), 'balance': round(balance, 2)} for date, balance in balance_series.items()]
        return jsonify(result)

    except Exception as e:
        print(f"Error getting historical balance: {e}")
        return jsonify({"error": f"Failed to get historical balance: {e}"}), 500



def get_company_logo(symbol, domain_fallback=None):
    """
    Fetch company logo using Finnhub API.
    Optionally fallback to Clearbit using the company's domain if Finnhub has no logo.
    """

    # 1. Try Finnhub logo
    finnhub_url = f"https://finnhub.io/api/logo?symbol={symbol}&token={FINNHUB_TOKEN}"
    try:
        resp = requests.get(finnhub_url).json()
        if resp and resp.get("url"):
            return resp["url"]
    except Exception as e:
        print(f"Finnhub logo fetch error for {symbol}: {e}")

    # 2. Optional fallback using Clearbit (requires domain)
    if domain_fallback:
        clearbit_url = f"https://logo.clearbit.com/{domain_fallback}"
        return clearbit_url

    # 3. No logo found
    return None

@portfolio_bp.route("/recommendationsandsentiment", methods=["GET"])
def recommendations_and_sentiment():
    """API endpoint to fetch portfolio stock recommendations, price targets, and sentiment."""
    user_id = request.args.get("user_id", 1)
    stocks = get_user_stocks(user_id)

    results = [get_finnhub_data(symbol) for symbol in stocks]
    #companies_logos = [get_company_logo(symbol) for symbol in stocks]  # Example for first symbol
    return jsonify(results)


def fetch_yahoo_news(symbols):
    """Fetch news from Yahoo Finance RSS feed and extract images from article pages"""
    base_url = "https://feeds.finance.yahoo.com/rss/2.0/headline"
    url = f"{base_url}?s={symbols}&region=US&lang=en-US"
    feed = feedparser.parse(url)
    
    def extract_image_from_page(article_url):
        """Extract the main image from the news article page"""
        try:
            from bs4 import BeautifulSoup
            import re
            
            # Set headers to mimic a real browser
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            # Fetch the article page with timeout
            response = requests.get(article_url, headers=headers, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Try different methods to find the main image
            image_url = None
            
            # Method 1: Look for Open Graph image
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                image_url = og_image['content']
            
            # Method 2: Look for Twitter card image
            if not image_url:
                twitter_image = soup.find('meta', attrs={'name': 'twitter:image'})
                if twitter_image and twitter_image.get('content'):
                    image_url = twitter_image['content']
            
            # Method 3: Look for article images (common patterns)
            if not image_url:
                # Look for images in article content
                article_selectors = [
                    'article img',
                    '.article-content img',
                    '.story-content img',
                    '.post-content img',
                    '.entry-content img',
                    '[data-module="ArticleBody"] img',
                    '.caas-body img'  # Yahoo Finance specific
                ]
                
                for selector in article_selectors:
                    img_tag = soup.select_one(selector)
                    if img_tag and img_tag.get('src'):
                        src = img_tag['src']
                        # Skip small images, icons, and ads
                        if not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'ad', 'banner']) and \
                           not src.endswith('.svg'):
                            image_url = src
                            break
            
            # Method 4: Look for the first significant image in the page
            if not image_url:
                all_images = soup.find_all('img')
                for img in all_images:
                    src = img.get('src', '')
                    if src and not any(skip in src.lower() for skip in ['icon', 'logo', 'avatar', 'ad', 'banner', 'pixel']) and \
                       not src.endswith('.svg'):
                        # Try to get image dimensions if available
                        width = img.get('width')
                        height = img.get('height')
                        if width and height:
                            try:
                                w, h = int(width), int(height)
                                if w >= 200 and h >= 150:  # Reasonable size for article image
                                    image_url = src
                                    break
                            except ValueError:
                                pass
                        else:
                            # If no dimensions, take the first reasonable image
                            image_url = src
                            break
            
            # Convert relative URLs to absolute URLs
            if image_url and image_url.startswith('/'):
                from urllib.parse import urljoin
                image_url = urljoin(article_url, image_url)
            
            return image_url
            
        except Exception as e:
            print(f"Error extracting image from {article_url}: {e}")
            return None
    
    articles = []
    for entry in feed.entries[:10]:
        # Extract image from the actual article page
        image_url = extract_image_from_page(entry.link)
        
        article = {
            "title": entry.title,
            "link": entry.link,
            "published": entry.published,
            "summary": entry.get("summary", ""),
            "category": "Market News"
        }
        
        # Only add image if one was found
        if image_url:
            article["image"] = image_url
            
        articles.append(article)
    
    return articles

@portfolio_bp.route("/news")
def get_news():
    """Get financial news with images extracted from article pages"""
    symbols = "^GSPC,BTC-USD,EURUSD=X"
    return jsonify(fetch_yahoo_news(symbols))