// Configuration file for Homebroker
// Replace 'YOUR_ALPHA_VANTAGE_API_KEY' with your actual Alpha Vantage API key
// Get your free API key from: https://www.alphavantage.co/support/#api-key

const CONFIG = {
    // Alpha Vantage API Configuration
    ALPHA_VANTAGE_API_KEY: 'YD0AVPAM5ADQLFPS',
    
    // Other API tokens 
    FINNHUB_API_TOKEN: 'd296b71r01qhoena6e2gd296b71r01qhoena6e30',
    
    // Backend API Configuration
    API_BASE: 'http://localhost:5000',
    
    // Search Configuration
    SEARCH_DEBOUNCE_MS: 300,
    MAX_SEARCH_RESULTS: 8,
    MIN_SEARCH_LENGTH: 2,
    
    // Chart Configuration
    DEFAULT_CHART_PERIOD: '1D',
    CHART_UPDATE_INTERVAL: 30000, // 30 seconds
    
    // Trading Configuration
    MIN_QUANTITY: 0.001,
    MAX_QUANTITY: 999999,
    PRICE_DECIMAL_PLACES: 2,
    
    // UI Configuration
    LOADING_TIMEOUT: 10000, // 10 seconds
    ERROR_DISPLAY_TIME: 5000, // 5 seconds
    
    // API Rate Limiting (Alpha Vantage free tier)
    API_CALLS_PER_MINUTE: 5,
    API_CALLS_PER_DAY: 500
};

// Validation function
function validateConfig() {
    const warnings = [];
    
    if (CONFIG.ALPHA_VANTAGE_API_KEY === 'YOUR_ALPHA_VANTAGE_API_KEY') {
        warnings.push('⚠️ Alpha Vantage API key not configured. Search will use fallback data.');
    }
    
    if (!CONFIG.API_BASE.startsWith('http')) {
        warnings.push('⚠️ API_BASE should start with http:// or https://');
    }
    
    if (warnings.length > 0) {
        console.warn('Configuration warnings:');
        warnings.forEach(warning => console.warn(warning));
    }
    
    return warnings.length === 0;
}

// Global API base URL for easy access
const API_BASE_URL = CONFIG.API_BASE;

// Export for use in other files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { CONFIG, validateConfig };
}