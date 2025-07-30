# 🔑 Alpha Vantage API Setup Guide

## Overview
The Homebroker uses Alpha Vantage API for real-time stock search functionality. This guide will help you set up your free API key.

## Step 1: Get Your Free API Key

1. **Visit Alpha Vantage**: Go to [https://www.alphavantage.co/support/#api-key](https://www.alphavantage.co/support/#api-key)

2. **Sign Up**: Fill out the form with:
   - Your email address
   - First and last name
   - Organization (can be "Personal" or "Individual")
   - Brief description of how you'll use the API

3. **Get Your Key**: After submitting, you'll receive your API key immediately on the page and via email.

## Step 2: Configure the Homebroker

1. **Open Configuration File**: Navigate to `client/config.js`

2. **Replace API Key**: Find this line:
   ```javascript
   ALPHA_VANTAGE_API_KEY: 'YOUR_ALPHA_VANTAGE_API_KEY',
   ```

3. **Update with Your Key**: Replace `YOUR_ALPHA_VANTAGE_API_KEY` with your actual API key:
   ```javascript
   ALPHA_VANTAGE_API_KEY: 'ABCD1234EFGH5678',  // Your actual key here
   ```

4. **Save the File**: Save `config.js` with your changes.

## Step 3: Test the Setup

1. **Open Homebroker**: Open `client/homebroker.html` in your web browser

2. **Test Search**: Type at least 2 characters in the search box (e.g., "AAPL")

3. **Verify Results**: You should see real stock search results from Alpha Vantage

4. **Check Console**: Open browser developer tools (F12) and check the console for any warnings

## API Limits (Free Tier)

Alpha Vantage free tier includes:
- **5 API requests per minute**
- **500 API requests per day**
- All core stock market data
- Real-time and historical data

## Troubleshooting

### ❌ "API key not configured" Warning
- **Problem**: You haven't replaced the placeholder API key
- **Solution**: Follow Step 2 above to set your actual API key

### ❌ "API call frequency" Error
- **Problem**: You've exceeded the 5 requests per minute limit
- **Solution**: Wait 1 minute before making more searches

### ❌ "Invalid API key" Error
- **Problem**: The API key is incorrect or expired
- **Solution**: Double-check your API key or generate a new one

### ❌ No Search Results
- **Problem**: API might be down or network issues
- **Solution**: The app will automatically fall back to mock data

## Advanced Configuration

You can customize other settings in `config.js`:

```javascript
const CONFIG = {
    // Search settings
    SEARCH_DEBOUNCE_MS: 300,        // Delay before searching (milliseconds)
    MAX_SEARCH_RESULTS: 8,          // Maximum results to show
    MIN_SEARCH_LENGTH: 2,           // Minimum characters to trigger search
    
    // API settings
    API_CALLS_PER_MINUTE: 5,        // Alpha Vantage free tier limit
    API_CALLS_PER_DAY: 500,         // Alpha Vantage free tier limit
};
```

## Fallback Behavior

If Alpha Vantage API is unavailable, the Homebroker will automatically:

1. **Try Backend API**: Attempt to use the Flask backend search
2. **Use Mock Data**: Fall back to a curated list of popular stocks
3. **Show Warning**: Display a console warning about the fallback

This ensures the application always works, even without API access.

## Security Notes

- **Client-Side Key**: The API key is stored in client-side JavaScript
- **Public Access**: Anyone who views the page source can see your key
- **Rate Limiting**: Alpha Vantage enforces rate limits per key
- **Free Tier**: The free tier is sufficient for personal use

For production applications, consider:
- Moving API calls to your backend server
- Implementing server-side API key management
- Adding user authentication and rate limiting

## Support

If you encounter issues:

1. **Check Browser Console**: Look for error messages in developer tools
2. **Verify API Key**: Ensure your key is correctly formatted
3. **Test API Directly**: Try your key at Alpha Vantage's documentation page
4. **Check Network**: Ensure you have internet connectivity

## Example API Response

A successful Alpha Vantage search returns data like this:

```json
{
    "bestMatches": [
        {
            "1. symbol": "AAPL",
            "2. name": "Apple Inc",
            "3. type": "Equity",
            "4. region": "United States",
            "5. marketOpen": "09:30",
            "6. marketClose": "16:00",
            "7. timezone": "UTC-04",
            "8. currency": "USD",
            "9. matchScore": "1.0000"
        }
    ]
}
```

This data is automatically parsed and displayed in the search results dropdown.