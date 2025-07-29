import yfinance as yf

def get_current_price(symbol):
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period='1d')
    if hist.empty:
        raise ValueError(f"No data found for symbol {symbol}")
    return round(hist['Close'][0], 2)
