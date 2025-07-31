#!/usr/bin/env python3
"""
Test script for the wallet API endpoint
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'server'))

from db import init_db
import yfinance as yf

def test_wallet_api():
    """Test the wallet API functionality"""
    try:
        print("🔍 Testing wallet API functionality...")
        conn = init_db()
        cursor = conn.cursor(dictionary=True)
        
        # Check if required tables exist
        print("\n📋 Checking database tables...")
        
        # Check users table
        cursor.execute("SHOW TABLES LIKE 'users'")
        if not cursor.fetchone():
            print("❌ Users table not found")
            return
        print("✅ Users table exists")
        
        # Check stocksportfolio table
        cursor.execute("SHOW TABLES LIKE 'stocksportfolio'")
        if not cursor.fetchone():
            print("❌ Stocksportfolio table not found")
            return
        print("✅ Stocksportfolio table exists")
        
        # Check stocks table
        cursor.execute("SHOW TABLES LIKE 'stocks'")
        if not cursor.fetchone():
            print("❌ Stocks table not found")
            return
        print("✅ Stocks table exists")
        
        # Get sample user
        cursor.execute("SELECT user_id, username FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if not user:
            print("❌ No users found in database")
            return
        
        user_id = user['user_id']
        username = user['username']
        print(f"📊 Testing with user: {username} (ID: {user_id})")
        
        # Check user's portfolio
        cursor.execute("""
            SELECT sp.symbol, sp.quantity, sp.avg_cost, s.name
            FROM stocksportfolio sp
            LEFT JOIN stocks s ON sp.symbol = s.symbol
            WHERE sp.user_id = %s AND sp.quantity > 0
        """, (user_id,))
        
        portfolio = cursor.fetchall()
        
        if not portfolio:
            print("⚠️  User has no stocks in portfolio")
            print("\n💡 To add test data:")
            print(f"INSERT INTO stocksportfolio (user_id, symbol, quantity, avg_cost) VALUES")
            print(f"({user_id}, 'AAPL', 10.0, 150.00),")
            print(f"({user_id}, 'MSFT', 5.0, 300.00);")
            return
        
        print(f"📈 User has {len(portfolio)} stocks in portfolio:")
        for stock in portfolio:
            print(f"  - {stock['symbol']}: {stock['quantity']} shares @ ${stock['avg_cost']}")
        
        # Test Yahoo Finance API for one stock
        test_symbol = portfolio[0]['symbol']
        print(f"\n🔍 Testing Yahoo Finance API for {test_symbol}...")
        
        try:
            ticker = yf.Ticker(test_symbol)
            hist = ticker.history(period="1d")
            
            if not hist.empty:
                current_price = float(hist['Close'][-1])
                print(f"✅ Current price for {test_symbol}: ${current_price:.2f}")
                
                # Test getting stock info
                info = ticker.info
                print(f"✅ Stock info retrieved: {info.get('longName', 'N/A')}")
                
            else:
                print(f"⚠️  No price data available for {test_symbol}")
                
        except Exception as yf_error:
            print(f"❌ Yahoo Finance error: {yf_error}")
        
        cursor.close()
        conn.close()
        
        print("\n🎯 Wallet API should work correctly!")
        print("Test the API endpoint: GET /wallet?user_id=" + str(user_id))
        
    except Exception as e:
        print(f"❌ Error: {e}")

def create_sample_data():
    """Create sample data for testing"""
    try:
        print("🔧 Creating sample data...")
        conn = init_db()
        cursor = conn.cursor()
        
        # Insert sample stocks if they don't exist
        sample_stocks = [
            ('AAPL', 'Apple Inc.', 150.00),
            ('MSFT', 'Microsoft Corporation', 300.00),
            ('GOOGL', 'Alphabet Inc.', 2500.00),
            ('TSLA', 'Tesla Inc.', 200.00),
            ('AMZN', 'Amazon.com Inc.', 3000.00)
        ]
        
        for symbol, name, price in sample_stocks:
            cursor.execute("""
                INSERT IGNORE INTO stocks (symbol, name, current_price) 
                VALUES (%s, %s, %s)
            """, (symbol, name, price))
        
        # Get first user
        cursor.execute("SELECT user_id FROM users LIMIT 1")
        user = cursor.fetchone()
        
        if user:
            user_id = user[0]
            
            # Insert sample portfolio data
            sample_portfolio = [
                (user_id, 'AAPL', 10.0, 145.00),
                (user_id, 'MSFT', 5.0, 295.00),
                (user_id, 'GOOGL', 2.0, 2450.00)
            ]
            
            for user_id, symbol, quantity, avg_cost in sample_portfolio:
                cursor.execute("""
                    INSERT INTO stocksportfolio (user_id, symbol, quantity, avg_cost) 
                    VALUES (%s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE 
                    quantity = VALUES(quantity), 
                    avg_cost = VALUES(avg_cost)
                """, (user_id, symbol, quantity, avg_cost))
            
            conn.commit()
            print("✅ Sample data created successfully")
        else:
            print("❌ No users found to create sample data")
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--create-sample":
        create_sample_data()
    else:
        test_wallet_api()
        print("\nTo create sample data, run: python test_wallet_api.py --create-sample")