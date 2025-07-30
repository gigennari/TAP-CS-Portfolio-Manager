from flask import Blueprint, request, jsonify
import yfinance as yf
import requests
import os
from datetime import datetime, timedelta
from db import init_db

portfolio_bp = Blueprint('portfolio', __name__)

# Alpha Vantage API configuration
ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YOUR_API_KEY_HERE')
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'


@portfolio_bp.route('/balance', methods=['GET'])
def get_balance():
    
    
    # Implementation for getting portfolio balance
    cursor = init_db().cursor(dictionary=True)
    user_id = request.args.get('user_id')
       
    cursor.execute("SELECT balance FROM accounts WHERE user_id = %s", (user_id,))
    return jsonify({"balance": 10000.00})

@portfolio_bp.route('/buy', methods=['POST'])
def buy_stock():
    # Implementation for buying stocks
    data = request.get_json()
    return jsonify({"success": True, "message": "Stock purchased successfully"})


@portfolio_bp.route('/sell', methods=['POST'])
def sell_stock():
    # Implementation for selling stocks
    data = request.get_json()
    return jsonify({"success": True, "message": "Stock sold successfully"})

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

@portfolio_bp.route('/trade', methods=['POST'])
def execute_trade():
    """Execute a trade order"""
    try:
        data = request.get_json()
        
        required_fields = ['symbol', 'action', 'quantity']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
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

@portfolio_bp.route('/portfolio', methods=['GET'])
def get_portfolio():
    """Get user's current portfolio"""
    # This would typically fetch from database
    # For now, return mock data
    portfolio = {
        "totalValue": 1234567.89,
        "totalChange": 28945.12,
        "totalChangePercent": 2.34,
        "positions": [
            {
                "symbol": "BTC-USD",
                "name": "Bitcoin",
                "quantity": 0.5234,
                "currentPrice": 67177.77,
                "totalValue": 35156.78,
                "change": 1234.56,
                "changePercent": 3.64
            },
            {
                "symbol": "SOL-USD", 
                "name": "Solana",
                "quantity": 15.67,
                "currentPrice": 187.50,
                "totalValue": 2938.13,
                "change": -45.23,
                "changePercent": -1.52
            }
        ]
    }
    
    return jsonify(portfolio)
