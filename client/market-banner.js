/**
 * Market Indices Banner Component
 * Displays a scrolling banner with real-time market data
 */

class MarketBanner {
    constructor() {
        this.indices = [];
        this.currentDisplayMode = 'percentage'; // 'percentage' or 'absolute'
        this.updateInterval = null;
        this.displayToggleInterval = null;
        this.isInitialized = false;
        
        this.init();
    }

    async init() {
        if (this.isInitialized) return;
        
        this.createBannerHTML();
        await this.fetchMarketData();
        this.startUpdateCycle();
        this.startDisplayToggle();
        
        this.isInitialized = true;
    }

    createBannerHTML() {
        // Create the banner container
        const bannerHTML = `
            <div id="marketBanner" class="fixed bottom-0 left-0 right-0 bg-gray-900 bg-opacity-90 backdrop-blur-sm border-t border-gray-700 overflow-hidden z-50">
                <div class="relative h-10 flex items-center">
                    <div id="marketTickerContainer" class="flex animate-scroll-seamless">
                        <div id="marketTicker" class="flex items-center space-x-8 whitespace-nowrap">
                            <!-- Market data will be populated here -->
                        </div>
                        <div class="w-16"></div>
                        <div id="marketTickerClone" class="flex items-center space-x-8 whitespace-nowrap">
                            <!-- Cloned market data for seamless scrolling -->
                        </div>
                    </div>
                </div>
                <div id="bannerLoading" class="absolute inset-0 flex items-center justify-center bg-gray-900 bg-opacity-90">
                    <div class="flex items-center space-x-2 text-gray-300">
                        <div class="w-4 h-4 border-2 border-gray-300 border-t-transparent rounded-full animate-spin"></div>
                        <span class="text-sm">Loading market data...</span>
                    </div>
                </div>
            </div>
        `;

        // Add CSS for scrolling animation
        const style = document.createElement('style');
        style.textContent = `
            @keyframes scroll-seamless {
                0% {
                    transform: translateX(0);
                }
                100% {
                    transform: translateX(-50%);
                }
            }
            
            .animate-scroll-seamless {
                animation: scroll-seamless 100s linear infinite;
                will-change: transform;
            }
            
            .animate-scroll-seamless:hover {
                animation-play-state: paused;
            }
            
            #marketBanner {
                transition: all 0.1s ease;
            }
            
            #marketTickerContainer {
                min-width: 200%;
                display: flex;
                align-items: center;
            }
            
            #marketTicker, #marketTickerClone {
                flex-shrink: 0;
            }
            
            /* Add bottom padding to body to prevent content from being hidden behind the fixed banner */
            body {
                padding-bottom: 40px !important;
            }
        `;
        document.head.appendChild(style);

        // Insert the banner at the end of the body (it will be positioned fixed at bottom)
        document.body.insertAdjacentHTML('beforeend', bannerHTML);
    }

    async fetchMarketData() {
        try {
            const response = await fetch('/marketsindices');
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            this.indices = data;
            this.updateBannerDisplay();
            
            // Hide loading indicator
            const loading = document.getElementById('bannerLoading');
            if (loading) {
                loading.style.display = 'none';
            }
            
        } catch (error) {
            console.error('Error fetching market data:', error);
            this.showErrorState();
        }
    }

    updateBannerDisplay() {
        const ticker = document.getElementById('marketTicker');
        const tickerClone = document.getElementById('marketTickerClone');
        const container = document.getElementById('marketTickerContainer');
        if (!ticker || !tickerClone || !this.indices.length) return;

        const tickerItems = this.indices.map(index => {
            const change = parseFloat(index.change) || 0;
            const changePercent = parseFloat(index.changePercent) || 0;
            const currentPrice = parseFloat(index.currentPrice) || 0;
            
            const isPositive = change >= 0;
            const colorClass = isPositive ? 'text-green-400' : 'text-red-400';
            const arrow = isPositive ? '▲' : '▼';
            
            // Format the display value based on current mode
            let displayValue;
            if (this.currentDisplayMode === 'percentage') {
                displayValue = `${changePercent >= 0 ? '+' : ''}${changePercent.toFixed(2)}%`;
            } else {
                displayValue = `${change >= 0 ? '+' : ''}${this.formatCurrency(change, index.currency)}`;
            }
            
            return `
                <div class="flex items-center space-x-2 px-6">
                    <span class="text-white font-medium text-sm">${index.name}</span>
                    <span class="text-gray-300 text-sm">${this.formatCurrency(currentPrice, index.currency)}</span>
                    <span class="${colorClass} text-sm font-medium flex items-center space-x-1">
                        <span class="text-xs">${arrow}</span>
                        <span>${displayValue}</span>
                    </span>
                </div>
            `;
        }).join('');

        // Temporarily pause animation during content update to prevent glitches
        if (container) {
            container.style.animationPlayState = 'paused';
        }
        
        // Update both the original and clone for seamless scrolling
        ticker.innerHTML = tickerItems;
        tickerClone.innerHTML = tickerItems;
        
        // Resume animation after a brief delay
        setTimeout(() => {
            if (container) {
                container.style.animationPlayState = 'running';
            }
        }, 50);
    }

    formatCurrency(value, currency = 'USD') {
        const num = parseFloat(value) || 0;
        
        // Special formatting for different asset types
        if (currency === 'USD') {
            if (num >= 1000000) {
                return `$${(num / 1000000).toFixed(2)}M`;
            } else if (num >= 1000) {
                return `$${(num / 1000).toFixed(2)}K`;
            } else {
                return `$${num.toFixed(2)}`;
            }
        } else {
            return `${num.toFixed(2)} ${currency}`;
        }
    }

    showErrorState() {
        const ticker = document.getElementById('marketTicker');
        const tickerClone = document.getElementById('marketTickerClone');
        const loading = document.getElementById('bannerLoading');
        
        const errorMessage = `
            <div class="flex items-center space-x-2 px-6">
                <span class="text-red-400 text-sm">⚠ Unable to load market data</span>
            </div>
        `;
        
        if (ticker) {
            ticker.innerHTML = errorMessage;
        }
        if (tickerClone) {
            tickerClone.innerHTML = errorMessage;
        }
        
        if (loading) {
            loading.style.display = 'none';
        }
    }

    startUpdateCycle() {
        // Update market data every 60 seconds
        this.updateInterval = setInterval(async () => {
            await this.fetchMarketData();
        }, 60000); 
    }

    startDisplayToggle() {
        // Toggle between percentage and absolute values every 3 seconds
        this.displayToggleInterval = setInterval(() => {
            this.currentDisplayMode = this.currentDisplayMode === 'percentage' ? 'absolute' : 'percentage';
            this.updateBannerDisplay();
        }, 3000);
    }

    destroy() {
        if (this.updateInterval) {
            clearInterval(this.updateInterval);
        }
        if (this.displayToggleInterval) {
            clearInterval(this.displayToggleInterval);
        }
        
        const banner = document.getElementById('marketBanner');
        if (banner) {
            banner.remove();
        }
        
        this.isInitialized = false;
    }
}

// Auto-initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    // Small delay to ensure header is rendered
    setTimeout(() => {
        window.marketBanner = new MarketBanner();
    }, 100);
});

// Export for manual initialization if needed
window.MarketBanner = MarketBanner;