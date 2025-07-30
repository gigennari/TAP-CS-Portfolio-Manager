// Performance Chart - Portfolio vs Fed Funds Rate
const performanceCtx = document.getElementById('performanceChart').getContext('2d');

// Sample data for the last 7 days
const dates = [];
const portfolioData = [];
const fedRateData = [];

// Generate sample data
for (let i = 6; i >= 0; i--) {
    const date = new Date();
    date.setDate(date.getDate() - i);
    dates.push(date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' }));
    
    // Sample portfolio performance (starting at 100, with some volatility)
    portfolioData.push(100 + Math.random() * 10 - 5 + (6 - i) * 0.5);
    
    // Fed funds rate (relatively stable around 5.25%)
    fedRateData.push(5.25 + Math.random() * 0.1 - 0.05);
}

new Chart(performanceCtx, {
    type: 'line',
    data: {
        labels: dates,
        datasets: [
            {
                label: 'Portfolio Performance (%)',
                data: portfolioData,
                borderColor: '#6366f1',
                backgroundColor: 'rgba(99, 102, 241, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#6366f1',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            },
            {
                label: 'Fed Funds Rate (%)',
                data: fedRateData,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.1)',
                borderWidth: 3,
                fill: false,
                tension: 0.4,
                pointBackgroundColor: '#ef4444',
                pointBorderColor: '#ffffff',
                pointBorderWidth: 2,
                pointRadius: 5
            }
        ]
    },
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
                labels: {
                    usePointStyle: true,
                    padding: 20,
                    font: {
                        size: 12,
                        weight: '500'
                    }
                }
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
                displayColors: true
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
                        return value.toFixed(1) + '%';
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

// Sector Allocation Pie Chart
const sectorCtx = document.getElementById('sectorChart').getContext('2d');

new Chart(sectorCtx, {
    type: 'doughnut',
    data: {
        labels: ['Bitcoin (BTC)', 'Solana (SOL)', 'Polkadot (DOT)', 'Bitcoin Cash (BCH)', 'Cardano (ADA)'],
        datasets: [{
            data: [45.2, 23.1, 15.7, 10.4, 5.6],
            backgroundColor: [
                '#f97316', // Orange for Bitcoin
                '#8b5cf6', // Purple for Solana
                '#ec4899', // Pink for Polkadot
                '#10b981', // Green for Bitcoin Cash
                '#3b82f6'  // Blue for Cardano
            ],
            borderWidth: 0,
            hoverOffset: 8
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
                backgroundColor: 'rgba(0, 0, 0, 0.8)',
                titleColor: '#ffffff',
                bodyColor: '#ffffff',
                borderColor: '#374151',
                borderWidth: 1,
                cornerRadius: 8,
                displayColors: true,
                callbacks: {
                    label: function(context) {
                        return context.label + ': ' + context.parsed + '%';
                    }
                }
            }
        },
        cutout: '60%',
        animation: {
            animateRotate: true,
            duration: 1000
        }
    }
});

// Add some interactivity to the table rows
document.addEventListener('DOMContentLoaded', function() {
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('mouseenter', function() {
            this.style.backgroundColor = '#f8fafc';
        });
        row.addEventListener('mouseleave', function() {
            this.style.backgroundColor = '';
        });
    });

    // Simulate real-time price updates
    function updatePrices() {
        const priceElements = document.querySelectorAll('tbody tr td:nth-child(5) div');
        priceElements.forEach(element => {
            const currentPrice = parseFloat(element.textContent.replace('$', '').replace(',', ''));
            const change = (Math.random() - 0.5) * 0.02; // ±1% change
            const newPrice = currentPrice * (1 + change);
            element.textContent = '$' + newPrice.toLocaleString('en-US', {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2
            });
        });
    }

    // Update prices every 30 seconds
    setInterval(updatePrices, 30000);
});

// Add smooth scrolling for better UX
document.documentElement.style.scrollBehavior = 'smooth';