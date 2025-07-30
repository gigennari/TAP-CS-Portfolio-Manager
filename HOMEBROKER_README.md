# 🏦 Homebroker - Stock Trading Platform

## Overview
The Homebroker is a comprehensive stock trading platform that allows users to search, analyze, and trade stocks with real-time data integration. It features auto-completion search using Alpha Vantage API and detailed stock information using Yahoo Finance.

## 🚀 Features

### 🔍 Stock Search & Discovery
- **Auto-completion Search**: Real-time stock symbol and company name search
- **Alpha Vantage Integration**: Comprehensive stock database search
- **Smart Filtering**: Search by symbol, company name, or keywords
- **Quick Selection**: Click-to-select from search results

### 📊 Stock Analysis
- **Real-time Data**: Current price, market cap, P/E ratio, volume
- **Interactive Charts**: Multiple time periods (1D, 5D, 1M, 3M, 1Y)
- **Technical Indicators**: 52-week high/low, dividend yield, beta
- **Company Information**: Sector, industry, detailed metrics

### 💹 Trading Functionality
- **Buy/Sell Orders**: Execute market and limit orders
- **Order Types**: Market orders and limit orders with custom pricing
- **Quantity Control**: Precise quantity input with decimal support
- **Cost Estimation**: Real-time total cost calculation
- **Order Confirmation**: Detailed confirmation before execution

### 📈 Portfolio Integration
- **Seamless Navigation**: Direct integration with portfolio dashboard
- **Position Tracking**: Automatic portfolio updates after trades
- **Performance Monitoring**: Track gains/losses across positions

## 🛠️ Technical Architecture

### Frontend (homebroker.html)
- **Framework**: Vanilla JavaScript with Tailwind CSS
- **Charts**: Chart.js for interactive stock price visualization
- **Responsive Design**: Mobile-first approach with grid layouts
- **Real-time Updates**: Live price updates and chart refreshing

### Backend (Flask API)
- **Framework**: Flask with CORS support
- **Data Sources**: 
  - Alpha Vantage API for stock search
  - Yahoo Finance (yfinance) for stock data and charts
- **Endpoints**:
  - `/search` - Stock symbol search
  - `/stock/<symbol>` - Detailed stock information
  - `/stock/<symbol>/history` - Historical price data
  - `/trade` - Execute buy/sell orders
  - `/portfolio` - Portfolio management

## 📋 Setup Instructions

### 1. Install Dependencies
```bash
# Run the setup script
python setup_homebroker.py

# Or install manually
pip install flask==2.3.2 flask-cors==4.0.0 yfinance==0.2.37 requests==2.31.0
```

### 2. Configure API Keys
1. Get a free Alpha Vantage API key from: https://www.alphavantage.co/support/#api-key
2. Update the `ALPHA_VANTAGE_API_KEY` in `server/.env` file

### 3. Start the Backend Server
```bash
cd server
python app.py
```
The server will start on `http://localhost:5000`

### 4. Open the Frontend
Open `client/homebroker.html` in your web browser

## 🎯 Usage Guide

### Searching for Stocks
1. Type in the search box (minimum 2 characters)
2. Select from auto-completion dropdown
3. Or press Enter/click Search button

### Viewing Stock Information
- **Overview Cards**: Key metrics at a glance
- **Interactive Chart**: Click period buttons to change timeframe
- **Stock Details**: Comprehensive company information

### Placing Orders
1. Select Buy or Sell action
2. Enter quantity (supports decimals)
3. Choose order type (Market or Limit)
4. Review estimated total
5. Click "Place Order" and confirm

## 🔧 API Integration

### Alpha Vantage API
- **Purpose**: Stock symbol search and discovery
- **Endpoint**: `SYMBOL_SEARCH` function
- **Rate Limit**: 5 API requests per minute (free tier)
- **Fallback**: Mock data when API unavailable

### Yahoo Finance API (yfinance)
- **Purpose**: Real-time stock data and historical prices
- **Data Points**: Price, volume, market cap, ratios, company info
- **Historical Data**: Multiple timeframes and intervals
- **Reliability**: Robust with built-in error handling

## 📊 Data Flow

```
User Input → Frontend → Flask API → External APIs → Database → Response → Frontend Display
```

1. **Search**: User types → Alpha Vantage API → Results displayed
2. **Stock Data**: Symbol selected → Yahoo Finance → Stock info displayed
3. **Charts**: Period selected → Historical data → Chart updated
4. **Trading**: Order placed → Validation → Execution → Portfolio updated

## 🎨 UI/UX Features

### Modern Design
- **Clean Interface**: Professional trading platform appearance
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Elements**: Hover effects, smooth animations
- **Loading States**: Clear feedback during API calls

### User Experience
- **Intuitive Navigation**: Clear flow from search to trade
- **Real-time Feedback**: Live price updates and calculations
- **Error Handling**: Graceful fallbacks and user-friendly messages
- **Accessibility**: Proper contrast ratios and semantic HTML

## 🔒 Security & Validation

### Input Validation
- **Symbol Validation**: Proper format checking
- **Quantity Limits**: Positive numbers only
- **Price Validation**: Reasonable price ranges
- **Order Validation**: Complete order information required

### API Security
- **CORS Configuration**: Proper cross-origin resource sharing
- **Rate Limiting**: Respectful API usage
- **Error Handling**: Secure error messages
- **Environment Variables**: API keys stored securely

## 📱 Mobile Responsiveness

### Responsive Breakpoints
- **Mobile**: Single column layout, touch-friendly buttons
- **Tablet**: Two-column layout, optimized spacing
- **Desktop**: Full three-column layout with side panels

### Touch Optimization
- **Button Sizes**: Minimum 44px touch targets
- **Gesture Support**: Swipe and tap interactions
- **Viewport Optimization**: Proper scaling and zooming

## 🚀 Performance Optimization

### Frontend Performance
- **Lazy Loading**: Charts loaded only when needed
- **Debounced Search**: Reduced API calls during typing
- **Caching**: Browser caching for static assets
- **Minification**: Optimized CSS and JavaScript

### Backend Performance
- **Connection Pooling**: Efficient database connections
- **Caching**: API response caching where appropriate
- **Error Recovery**: Graceful handling of API failures
- **Async Operations**: Non-blocking API calls

## 🔮 Future Enhancements

### Advanced Features
- **Watchlists**: Save and monitor favorite stocks
- **Alerts**: Price and volume alerts
- **Technical Analysis**: Advanced charting tools
- **News Integration**: Real-time financial news
- **Options Trading**: Support for options contracts

### Portfolio Features
- **Performance Analytics**: Detailed portfolio analysis
- **Risk Assessment**: Portfolio risk metrics
- **Rebalancing**: Automated portfolio rebalancing
- **Tax Reporting**: Capital gains/losses reporting

### Social Features
- **Community**: Social trading features
- **Copy Trading**: Follow successful traders
- **Discussion**: Stock discussion forums
- **Ratings**: Community stock ratings

## 🐛 Troubleshooting

### Common Issues
1. **API Key Error**: Ensure Alpha Vantage API key is set correctly
2. **CORS Issues**: Check Flask CORS configuration
3. **Chart Not Loading**: Verify Chart.js CDN availability
4. **Search Not Working**: Check network connectivity and API limits

### Debug Mode
Enable debug mode in Flask for detailed error messages:
```python
app.run(debug=True)
```

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review API documentation
3. Check browser console for errors
4. Verify all dependencies are installed

## 📄 License

This project is part of the Portfolio Manager Team 19 application.