# Configuration file for Python backend
import os

class Config:
    # Alpha Vantage API Configuration
    ALPHA_VANTAGE_API_KEY = os.getenv('ALPHA_VANTAGE_API_KEY', 'YD0AVPAM5ADQLFPS')
    ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
    
    # Finnhub API Configuration
    FINNHUB_API_TOKEN = os.getenv('FINNHUB_API_TOKEN', 'd296b71r01qhoena6e2gd296b71r01qhoena6e30')
    FINNHUB_BASE_URL = 'https://finnhub.io/api/v1'
    
    # Database Configuration
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_USER = os.getenv('DB_USER', 'root')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'n3u3da!')
    DB_NAME = os.getenv('DB_NAME', 'bygdb')
    
    # API Configuration
    API_BASE = 'http://localhost:5000'
    
    # Search Configuration
    SEARCH_DEBOUNCE_MS = 300
    MAX_SEARCH_RESULTS = 8
    MIN_SEARCH_LENGTH = 2
    
    # Chart Configuration
    DEFAULT_CHART_PERIOD = '1D'
    CHART_UPDATE_INTERVAL = 30000  # 30 seconds
    
    # Trading Configuration
    MIN_QUANTITY = 0.001
    MAX_QUANTITY = 999999
    PRICE_DECIMAL_PLACES = 2
    
    # UI Configuration
    LOADING_TIMEOUT = 10000  # 10 seconds
    ERROR_DISPLAY_TIME = 5000  # 5 seconds
    
    # API Rate Limiting
    API_CALLS_PER_MINUTE = 5
    API_CALLS_PER_DAY = 500

# Create a global config instance
CONFIG = Config()

# Random stocks for fallback
RANDOM_STOCKS = [
    'AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 
    'META', 'NVDA', 'NFLX', 'AMD', 'INTC'
]