from flask import Blueprint, request, jsonify
import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from db import init_db, dump_db
from time import sleep
import plotly.graph_objects as go #built on javascript, can be used on front end 
from plotly.subplots import make_subplots
import pandas as pd


portfolio_bp = Blueprint('portfolio', __name__)

# Alpha Vantage config
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YD0AVPAM5ADQLFPS')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'


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
            print(symbol)
            quantity = float(stock['quantity'])
            avg_cost = float(stock['avg_cost']) if stock['avg_cost'] else 0.00
            name = stock.get('company_name', symbol)

            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="7d")

                current_price = float(hist['Close'][-1]) if not hist.empty else 0.00
                price_24h = float(hist['Close'][-2]) if len(hist) > 1 else current_price
                price_7d = float(hist['Close'][0]) if len(hist) > 0 else current_price

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
        
        required_fields = ['user_id', 'symbol', 'action', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        user_id = data['user_id']
        symbol = data['symbol'].upper()
        action = data['action'].lower()  # 'buy' or 'sell'
        quantity = float(data['quantity'])
        order_type = data.get('orderType', 'market')
        limit_price = data.get('limitPrice')
        
        if action not in ['buy', 'sell']:
            return jsonify({"error": "Action must be 'buy' or 'sell'"}), 400
        
        if quantity <= 0:
            return jsonify({"error": "Quantity must be positive"}), 400
        
        # Get current stock price for validation
        ticker = yf.Ticker(symbol)
        current_price = ticker.info.get('currentPrice', ticker.info.get('regularMarketPrice', 0))
        
        if not current_price:
            return jsonify({"error": "Unable to get current stock price"}), 400
        
        # Calculate trade value
        trade_price = limit_price if order_type == 'limit' and limit_price else current_price
        trade_value = quantity * trade_price
        
        # Here you would typically:
        # 1. Check user's account balance (for buy orders)
        # 2. Check user's stock holdings (for sell orders)
        # 3. Execute the trade through a broker API
        # 4. Update the user's portfolio in the database
        
        # For now, we'll simulate a successful trade
        order_id = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{symbol}"
        
        trade_result = {
            "success": True,
            "orderId": order_id,
            "user_id": user_id,
            "symbol": symbol,
            "action": action,
            "quantity": quantity,
            "price": trade_price,
            "totalValue": trade_value,
            "orderType": order_type,
            "timestamp": datetime.now().isoformat(),
            "status": "executed"
        }
        
        return jsonify(trade_result)
        
    except ValueError as e:
        return jsonify({"error": "Invalid quantity or price format"}), 400
    except Exception as e:
        print(f"Error executing trade: {e}")
        return jsonify({"error": "Failed to execute trade"}), 500

    
#buy stock -> update stocksportfolio qty and avg cost (include symbol if not there yet), update accounts balance, update stcoks table if we don't have the symbol there yet,  
def buy_stock():
    # Implementation for buying stocks
    data = request.get_json()
    return jsonify({"success": True, "message": "Stock purchased successfully"})

#(if qty = 0, delete)
def sell_stock():
    # Implementation for selling stocks
    data = request.get_json()
    return jsonify({"success": True, "message": "Stock sold successfully"})


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
            return jsonify({})
        
        historical_data = {}
        
        for stock in portfolio_stocks[0:1]:
            symbol = stock['symbol']
            quantity = float(stock['quantity'])
            avg_cost = float(stock['avg_cost']) if stock['avg_cost'] else 0.00
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1y")
            
            for date, row in hist.iterrows():
                date_str = date.strftime("%Y-%m-%d")
                close_price = float(row["Close"]) if not pd.isna(row["Close"]) else 0.00
                value = close_price * quantity
                historical_data[date_str] = historical_data.get(date_str, 0.00) + value
            
    except Exception as e:
        print(f"Error getting historical data: {e}")
        return jsonify({"error": f"Failed to get historical data {e}"}), 500
            
            
