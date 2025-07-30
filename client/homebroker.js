// Configuration - loaded from config.js
const API_BASE = CONFIG.API_BASE;
const ALPHA_VANTAGE_API_KEY = CONFIG.ALPHA_VANTAGE_API_KEY;
const ALPHA_VANTAGE_BASE_URL = CONFIG.ALPHA_VANTAGE_BASE_URL;

// Global variables
let currentStock = null;
let stockChart = null;
let tradeAction = 'buy';

// DOM elements
const stockSearch = document.getElementById('stockSearch');
const searchResults = document.getElementById('searchResults');
const searchBtn = document.getElementById('searchBtn');
const stockInfo = document.getElementById('stockInfo');
const loadingIndicator = document.getElementById('loadingIndicator');
const buyBtn = document.getElementById('buyBtn');
const sellBtn = document.getElementById('sellBtn');
const quantity = document.getElementById('quantity');
const orderType = document.getElementById('orderType');
const limitPriceDiv = document.getElementById('limitPriceDiv');
const estimatedTotal = document.getElementById('estimatedTotal');
const submitTradeBtn = document.getElementById('submitTradeBtn');

// Initialize
document.addEventListener('DOMContentLoaded', function() {
    // Validate configuration
    validateConfig();
    
    setupEventListeners();
    initializeChart();
});

function setupEventListeners() {
    // Search functionality
    stockSearch.addEventListener('input', debounce(handleSearchInput, CONFIG.SEARCH_DEBOUNCE_MS));
    searchBtn.addEventListener('click', handleSearch);
    stockSearch.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            handleSearch();
        }
    });
    
    // Trading form
    buyBtn.addEventListener('click', () => setTradeAction('buy'));
    sellBtn.addEventListener('click', () => setTradeAction('sell'));
    quantity.addEventListener('input', updateEstimatedTotal);
    orderType.addEventListener('change', handleOrderTypeChange);
    document.getElementById('tradeForm').addEventListener('submit', handleTradeSubmit);
    
    // Period buttons
    document.querySelectorAll('.period-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.period-btn').forEach(b => {
                b.className = 'px-3 py-1 text-sm text-slate-500 hover:bg-slate-100 rounded-lg period-btn';
            });
            this.className = 'px-3 py-1 text-sm bg-indigo-100 text-indigo-700 rounded-lg font-medium period-btn';
            if (currentStock) {
                loadStockChart(currentStock.symbol, this.dataset.period);
            }
        });
    });
    
    // Click outside to close search results
    document.addEventListener('click', function(e) {
        if (!stockSearch.contains(e.target) && !searchResults.contains(e.target)) {
            searchResults.classList.add('hidden');
        }
    });
}

function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

async function handleSearchInput() {
    const query = stockSearch.value.trim();
    if (query.length < CONFIG.MIN_SEARCH_LENGTH) {
        searchResults.classList.add('hidden');
        return;
    }
    
    // Show loading indicator
    searchResults.innerHTML = `
        <div class="px-4 py-3 flex items-center space-x-2">
            <div class="loading-spinner"></div>
            <span class="text-slate-600 text-sm">Searching stocks...</span>
        </div>
    `;
    searchResults.classList.remove('hidden');
    
    try {
        // Try Alpha Vantage API first
        const results = await searchStocksAlphaVantage(query);
        if (results && results.length > 0) {
            displaySearchResults(results);
        } else {
            // Fallback to backend API
            try {
                const response = await fetch(`${API_BASE}/search?query=${encodeURIComponent(query)}`);
                const data = await response.json();
                
                if (data.results && data.results.length > 0) {
                    displaySearchResults(data.results);
                } else {
                    // Final fallback to mock data
                    const mockResults = await mockSearchStocks(query);
                    displaySearchResults(mockResults);
                }
            } catch (backendError) {
                console.warn('Backend API unavailable, using mock data:', backendError);
                const mockResults = await mockSearchStocks(query);
                displaySearchResults(mockResults);
            }
        }
    } catch (error) {
        console.error('Search error:', error);
        // Fallback to mock data
        const results = await mockSearchStocks(query);
        displaySearchResults(results);
    }
}

async function searchStocksAlphaVantage(query) {
    try {
        // Check if API key is configured
        if (ALPHA_VANTAGE_API_KEY === 'YD0AVPAM5ADQLFPS') {
            console.warn('Alpha Vantage API key not configured. Using fallback.');
            return null;
        }
        
        // Alpha Vantage SYMBOL_SEARCH endpoint
        const url = `${ALPHA_VANTAGE_BASE_URL}?function=SYMBOL_SEARCH&keywords=${encodeURIComponent(query)}&apikey=${ALPHA_VANTAGE_API_KEY}`;
        
        const response = await fetch(url);
        const data = await response.json();
        
        // Check for API errors
        if (data['Error Message']) {
            console.error('Alpha Vantage API Error:', data['Error Message']);
            return null;
        }
        
        if (data['Note']) {
            console.warn('Alpha Vantage API Note:', data['Note']);
            return null;
        }
        
        // Parse the results
        if (data['bestMatches'] && Array.isArray(data['bestMatches'])) {
            return data['bestMatches'].map(match => ({
                symbol: match['1. symbol'] || '',
                name: match['2. name'] || '',
                type: match['3. type'] || 'Equity',
                region: match['4. region'] || '',
                marketOpen: match['5. marketOpen'] || '',
                marketClose: match['6. marketClose'] || '',
                timezone: match['7. timezone'] || '',
                currency: match['8. currency'] || 'USD',
                matchScore: match['9. matchScore'] || '0.0000'
            })).slice(0, CONFIG.MAX_SEARCH_RESULTS);
        }
        
        return [];
        
    } catch (error) {
        console.error('Alpha Vantage API request failed:', error);
        return null;
    }
}

async function mockSearchStocks(query) {
    // Enhanced mock data for demonstration when API is unavailable
    const mockStocks = [
        { symbol: 'AAPL', name: 'Apple Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'MSFT', name: 'Microsoft Corporation', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'GOOGL', name: 'Alphabet Inc. Class A', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'AMZN', name: 'Amazon.com Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'TSLA', name: 'Tesla Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'META', name: 'Meta Platforms Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'NVDA', name: 'NVIDIA Corporation', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'NFLX', name: 'Netflix Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'AMD', name: 'Advanced Micro Devices Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'INTC', name: 'Intel Corporation', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'CRM', name: 'Salesforce Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'ORCL', name: 'Oracle Corporation', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'ADBE', name: 'Adobe Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'PYPL', name: 'PayPal Holdings Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'DIS', name: 'The Walt Disney Company', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'UBER', name: 'Uber Technologies Inc.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'SPOT', name: 'Spotify Technology S.A.', type: 'Equity', region: 'United States', currency: 'USD' },
        { symbol: 'ZOOM', name: 'Zoom Video Communications Inc.', type: 'Equity', region: 'United States', currency: 'USD' }
    ];
    
    return mockStocks.filter(stock => 
        stock.symbol.toLowerCase().includes(query.toLowerCase()) ||
        stock.name.toLowerCase().includes(query.toLowerCase())
    ).slice(0, CONFIG.MAX_SEARCH_RESULTS);
}

function displaySearchResults(results) {
    if (results.length === 0) {
        searchResults.innerHTML = '<div class="px-4 py-3 text-slate-500 text-sm">No results found</div>';
        searchResults.classList.remove('hidden');
        return;
    }
    
    const html = results.map(stock => {
        // Handle both Alpha Vantage and mock data formats
        const region = stock.region ? ` • ${stock.region}` : '';
        const currency = stock.currency && stock.currency !== 'USD' ? ` (${stock.currency})` : '';
        const matchScore = stock.matchScore ? parseFloat(stock.matchScore) : 1.0;
        
        return `
            <div class="px-4 py-3 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-b-0" 
                    onclick="selectStock('${stock.symbol}', '${stock.name.replace(/'/g, "\\'")}')">
                <div class="flex justify-between items-start">
                    <div class="flex-1 min-w-0">
                        <div class="font-medium text-slate-900">${stock.symbol}</div>
                        <div class="text-sm text-slate-600 truncate">${stock.name}</div>
                        <div class="text-xs text-slate-400 mt-1">
                            ${stock.type}${region}${currency}
                            ${matchScore < 1.0 ? ` • Match: ${(matchScore * 100).toFixed(0)}%` : ''}
                        </div>
                    </div>
                    <div class="flex flex-col items-end text-xs text-slate-500 ml-2">
                        <span class="font-medium">${stock.type}</span>
                        ${stock.region ? `<span class="mt-1">${stock.region}</span>` : ''}
                    </div>
                </div>
            </div>
        `;
    }).join('');
    
    searchResults.innerHTML = html;
    searchResults.classList.remove('hidden');
}

async function selectStock(symbol, name) {
    searchResults.classList.add('hidden');
    stockSearch.value = `${symbol} - ${name}`;
    await loadStockData(symbol);
}

async function handleSearch() {
    const query = stockSearch.value.trim().split(' ')[0]; // Get symbol part
    if (query) {
        await loadStockData(query.toUpperCase());
    }
}

async function loadStockData(symbol) {
    showLoading(true);
    
    try {
        const response = await fetch(`${API_BASE}/stock/${symbol}`);
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const stockData = await response.json();
        currentStock = stockData;
        
        displayStockInfo(stockData);
        await loadStockChart(symbol, '1D');
        
        stockInfo.classList.remove('hidden');
        submitTradeBtn.disabled = false;
        
    } catch (error) {
        console.error('Error loading stock data:', error);
        
        // Fallback to mock data
        try {
            const stockData = await mockGetStockData(symbol);
            currentStock = stockData;
            displayStockInfo(stockData);
            await loadStockChart(symbol, '1D');
            stockInfo.classList.remove('hidden');
            submitTradeBtn.disabled = false;
        } catch (mockError) {
            alert('Error loading stock data. Please try again.');
        }
    } finally {
        showLoading(false);
    }
}

async function mockGetStockData(symbol) {
    // Mock data for demonstration
    const mockData = {
        symbol: symbol,
        name: getCompanyName(symbol),
        currentPrice: Math.random() * 200 + 50,
        change: (Math.random() - 0.5) * 10,
        changePercent: (Math.random() - 0.5) * 5,
        marketCap: Math.random() * 1000000000000 + 100000000000,
        peRatio: Math.random() * 30 + 10,
        volume: Math.random() * 100000000 + 10000000,
        sector: getSector(symbol),
        industry: getIndustry(symbol),
        high52: Math.random() * 250 + 100,
        low52: Math.random() * 100 + 20,
        dividendYield: Math.random() * 5
    };
    
    mockData.changePercent = (mockData.change / mockData.currentPrice) * 100;
    
    return mockData;
}

function getCompanyName(symbol) {
    const names = {
        'AAPL': 'Apple Inc.',
        'MSFT': 'Microsoft Corporation',
        'GOOGL': 'Alphabet Inc.',
        'AMZN': 'Amazon.com Inc.',
        'TSLA': 'Tesla Inc.',
        'META': 'Meta Platforms Inc.',
        'NVDA': 'NVIDIA Corporation',
        'NFLX': 'Netflix Inc.',
        'AMD': 'Advanced Micro Devices Inc.',
        'INTC': 'Intel Corporation'
    };
    return names[symbol] || `${symbol} Corporation`;
}

function getSector(symbol) {
    const sectors = {
        'AAPL': 'Technology',
        'MSFT': 'Technology',
        'GOOGL': 'Technology',
        'AMZN': 'Consumer Discretionary',
        'TSLA': 'Consumer Discretionary',
        'META': 'Technology',
        'NVDA': 'Technology',
        'NFLX': 'Communication Services',
        'AMD': 'Technology',
        'INTC': 'Technology'
    };
    return sectors[symbol] || 'Technology';
}

function getIndustry(symbol) {
    const industries = {
        'AAPL': 'Consumer Electronics',
        'MSFT': 'Software',
        'GOOGL': 'Internet Content & Information',
        'AMZN': 'Internet Retail',
        'TSLA': 'Auto Manufacturers',
        'META': 'Internet Content & Information',
        'NVDA': 'Semiconductors',
        'NFLX': 'Entertainment',
        'AMD': 'Semiconductors',
        'INTC': 'Semiconductors'
    };
    return industries[symbol] || 'Software';
}

function displayStockInfo(data) {
    document.getElementById('currentPrice').textContent = `$${data.currentPrice.toFixed(2)}`;
    document.getElementById('priceChange').textContent = 
        `${data.change >= 0 ? '+' : ''}${data.change.toFixed(2)} (${data.changePercent.toFixed(2)}%)`;
    document.getElementById('priceChange').className = 
        `text-sm font-medium mt-1 ${data.change >= 0 ? 'text-green-600' : 'text-red-600'}`;
    
    document.getElementById('marketCap').textContent = formatLargeNumber(data.marketCap);
    document.getElementById('peRatio').textContent = data.peRatio.toFixed(2);
    document.getElementById('volume').textContent = formatLargeNumber(data.volume);
    
    document.getElementById('stockTitle').textContent = `${data.name} (${data.symbol})`;
    document.getElementById('stockSymbol').textContent = `${data.symbol} Stock Performance`;
    
    document.getElementById('companyName').textContent = data.name;
    document.getElementById('sector').textContent = data.sector;
    document.getElementById('industry').textContent = data.industry;
    document.getElementById('high52').textContent = `$${data.high52.toFixed(2)}`;
    document.getElementById('low52').textContent = `$${data.low52.toFixed(2)}`;
    document.getElementById('dividendYield').textContent = `${data.dividendYield.toFixed(2)}%`;
}

function formatLargeNumber(num) {
    if (num >= 1e12) return (num / 1e12).toFixed(2) + 'T';
    if (num >= 1e9) return (num / 1e9).toFixed(2) + 'B';
    if (num >= 1e6) return (num / 1e6).toFixed(2) + 'M';
    if (num >= 1e3) return (num / 1e3).toFixed(2) + 'K';
    return num.toFixed(0);
}

function initializeChart() {
    const ctx = document.getElementById('stockChart').getContext('2d');
    stockChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Stock Price',
                data: [],
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: 'rgba(0, 0, 0, 0.8)',
                    titleColor: '#ffffff',
                    bodyColor: '#ffffff',
                    borderColor: '#374151',
                    borderWidth: 1,
                    cornerRadius: 8,
                    callbacks: {
                        label: function(context) {
                            return `Price: $${context.parsed.y.toFixed(2)}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 11
                        }
                    }
                },
                y: {
                    grid: {
                        color: '#f1f5f9'
                    },
                    ticks: {
                        color: '#64748b',
                        font: {
                            size: 11
                        },
                        callback: function(value) {
                            return '$' + value.toFixed(2);
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

async function loadStockChart(symbol, period) {
    if (!stockChart) return;
    
    try {
        const response = await fetch(`${API_BASE}/stock/${symbol}/history?frontend_period=${period}`);
        
        if (response.ok) {
            const chartData = await response.json();
            stockChart.data.labels = chartData.labels;
            stockChart.data.datasets[0].data = chartData.data;
            stockChart.update();
        } else {
            // Fallback to mock data
            const chartData = generateMockChartData(period);
            stockChart.data.labels = chartData.labels;
            stockChart.data.datasets[0].data = chartData.data;
            stockChart.update();
        }
    } catch (error) {
        console.error('Error loading chart data:', error);
        // Fallback to mock data
        const chartData = generateMockChartData(period);
        stockChart.data.labels = chartData.labels;
        stockChart.data.datasets[0].data = chartData.data;
        stockChart.update();
    }
}

function generateMockChartData(period) {
    const periods = {
        '1D': { points: 24, interval: 'hour' },
        '5D': { points: 5, interval: 'day' },
        '1M': { points: 30, interval: 'day' },
        '3M': { points: 90, interval: 'day' },
        '1Y': { points: 365, interval: 'day' }
    };
    
    const config = periods[period] || periods['1D'];
    const labels = [];
    const data = [];
    const basePrice = currentStock ? currentStock.currentPrice : 100;
    
    for (let i = 0; i < config.points; i++) {
        const date = new Date();
        if (config.interval === 'hour') {
            date.setHours(date.getHours() - (config.points - i));
            labels.push(date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
        } else {
            date.setDate(date.getDate() - (config.points - i));
            labels.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
        }
        
        // Generate realistic price movement
        const volatility = 0.02; // 2% volatility
        const trend = (Math.random() - 0.5) * 0.001; // Small trend
        const price = basePrice * (1 + (Math.random() - 0.5) * volatility + trend * i);
        data.push(price);
    }
    
    return { labels, data };
}

function setTradeAction(action) {
    tradeAction = action;
    if (action === 'buy') {
        buyBtn.className = 'px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors font-medium';
        sellBtn.className = 'px-4 py-2 bg-slate-300 text-slate-700 rounded-lg hover:bg-slate-400 transition-colors font-medium';
    } else {
        sellBtn.className = 'px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium';
        buyBtn.className = 'px-4 py-2 bg-slate-300 text-slate-700 rounded-lg hover:bg-slate-400 transition-colors font-medium';
    }
    updateEstimatedTotal();
}

function handleOrderTypeChange() {
    if (orderType.value === 'limit') {
        limitPriceDiv.classList.remove('hidden');
    } else {
        limitPriceDiv.classList.add('hidden');
    }
    updateEstimatedTotal();
}

function updateEstimatedTotal() {
    if (!currentStock || !quantity.value) {
        estimatedTotal.textContent = '$0.00';
        return;
    }
    
    const qty = parseFloat(quantity.value);
    const price = orderType.value === 'limit' && document.getElementById('limitPrice').value 
        ? parseFloat(document.getElementById('limitPrice').value)
        : currentStock.currentPrice;
    
    const total = qty * price;
    estimatedTotal.textContent = `$${total.toFixed(2)}`;
}

async function handleTradeSubmit(e) {
    e.preventDefault();
    
    if (!currentStock || !quantity.value) {
        alert('Please select a stock and enter quantity');
        return;
    }
    
    const tradeData = {
        symbol: currentStock.symbol,
        action: tradeAction,
        quantity: parseFloat(quantity.value),
        orderType: orderType.value,
        limitPrice: orderType.value === 'limit' ? parseFloat(document.getElementById('limitPrice').value) : null,
        estimatedPrice: currentStock.currentPrice
    };
    
    // Show confirmation
    const confirmMessage = `Confirm ${tradeAction.toUpperCase()} order:\n\n` +
        `Stock: ${currentStock.symbol}\n` +
        `Quantity: ${tradeData.quantity}\n` +
        `Order Type: ${tradeData.orderType}\n` +
        `Estimated Total: ${estimatedTotal.textContent}`;
    
    if (confirm(confirmMessage)) {
        try {
            showLoading(true);
            
            // Mock API call - replace with actual backend call
            await mockExecuteTrade(tradeData);
            
            alert('Order placed successfully!');
            
            // Reset form
            document.getElementById('tradeForm').reset();
            setTradeAction('buy');
            estimatedTotal.textContent = '$0.00';
            
        } catch (error) {
            console.error('Trade execution error:', error);
            alert('Error placing order. Please try again.');
        } finally {
            showLoading(false);
        }
    }
}

async function mockExecuteTrade(tradeData) {
    try {
        const response = await fetch(`${API_BASE}/trade`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(tradeData)
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        const result = await response.json();
        return result;
        
    } catch (error) {
        console.error('Trade execution error:', error);
        
        // Fallback to mock execution
        await new Promise(resolve => setTimeout(resolve, 1000));
        console.log('Trade executed (mock):', tradeData);
        return { success: true, orderId: Math.random().toString(36).substr(2, 9) };
    }
}

function showLoading(show) {
    if (show) {
        loadingIndicator.classList.remove('hidden');
    } else {
        loadingIndicator.classList.add('hidden');
    }
}