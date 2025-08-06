# TAP-CS-Portfolio-Manager

# Set Up 

## Running server
```bash
cd server
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
pip install yfinance --upgrade --no-cache-dir
python app.py
```

## Running client
After running the server, open ``localhost:5000`` in your browser.

## Dumping the database to a file
Run this command on bash:
```bash
& "C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe" -u root -p bygDB > latest_dump.sql

```

# Our Database Structure
![database structure]()



# The Application 


## The Portfolio 

![Portfolio Dashboard](screenshots/portfolio.jpeg)

This page provides a comprehensive view of a user's **equity portfolio**.  
It lists all stocks currently held, their performance, transaction history, and sector allocation.  
The dashboard is designed to help users track **portfolio value**, **daily changes**, and **cumulative returns** over time.

---

The Portfolio Dashboard is divided into several sections:

#### **1. Header Tiles (Summary Cards)**

- **Account Balance**  
  - Displays the **available cash** in the user's account.  
  - This balance is included in profit calculations but **cannot be transferred from or to other accounts**.

- **Total Portfolio Value**  
  - Shows the **total market value of all invested assets** for the current day.  
  - **Formula:**  
    ```text
    Total Portfolio Value = Σ(Market Value of each Stock)
    ```  
  - Market value is updated using **Yahoo Finance historical data** via `ticker.history()`.

- **24h Change**  
  - Displays the **profit/loss** considering the **change in total portfolio value** since yesterday.

---

## Home Broker

### 🔍 Stock Search

![Stock Search](screenshots/homebroker-search.png)

The **search functionality** enables users to find stocks and funds by ticker symbol or company name.

- The search uses the [Alpha Vantage API](https://www.alphavantage.co/documentation/#symbolsearch) `SYMBOL_SEARCH` endpoint to retrieve matching securities in real time.
- Results display:
  - Ticker symbol
  - Company or fund name
  - Instrument type (Equity or Mutual Fund)
  - Country of listing

Example: Searching for `dis` shows options like:
- `DIS` — Walt Disney Co (Equity, United States)
- `DIS.LON` — Distil Plc (Equity, UK)
- `DISAX` — BNY Mellon International Stock Fund (Mutual Fund, US)


After selecting a stock, the page shows detailed information:

#### **Header Metrics**
- **Current Price**
  - Live price of the security
  - Includes change and % movement for the day
- **Market Cap**
  - Total market capitalization
- **P/E Ratio**
  - Price-to-earnings ratio
- **Volume**
  - Daily trading volume

#### **Performance Chart**
- Interactive price chart with selectable timeframes:
  - 1D (1 day)
  - 5D (5 days)
  - 1M (1 month)
  - 3M (3 months)
  - 1Y (1 year)

#### **Stock Details Panel**
- Company name and sector
- Industry classification
- 52-week high and low
- Dividend yield

Example for Disney (DIS):
- Sector: Communication Services
- Industry: Entertainment
- 52W High: $124.69
- 52W Low: $80.10
- Dividend Yield: 0.85%

---

### 🛒 Trading Stocks

At the bottom right, the **Trade Stock** panel allows placing buy or sell orders.

#### **Buy Mode**

![Buying](screenshots/homebroker-buy.jpeg)

- When **Buy** is selected:
  - You can enter the quantity to purchase
  - Choose the order type (e.g., Market Order)
  - Estimated total updates based on current price × quantity
  - **Place Order** button finalizes the trade
  -If you don't have sufficient funds, an error message appears

  

#### **Sell Mode**

![Buying](screenshots/homebroker-sell.jpeg)

- When **Sell** is selected:
  - The panel shows:
    - **Your Holdings** — e.g., “5 shares” currently owned
  - Quantity input to specify how many shares to sell
  - Order type selector
  - Estimated proceeds display dynamically
  - **Place Order** button executes the sell order
  -If you don't have enough shares, an error message appears




---

## News 

## 📊 Market Indices Banner  

| Market Type          | Index / Pair         | Number of Constituents | Weighting Method        | Sector / Asset Focus            | Volatility    |
| -------------------- | -------------------- | ---------------------- | ----------------------- | ------------------------------- | ------------- |
| 📈 **US Stock Market**  | **NASDAQ Composite** | 3,000+                 | Market-cap weighted     | Tech-heavy (growth & biotech)   | High          |
| 📈 **US Stock Market**  | **S\&P 500**         | 500                    | Market-cap (free-float) | Broad multi-sector (11 sectors) | Moderate      |
| 📈 **US Stock Market**  | **Dow Jones (DJIA)** | 30                     | Price-weighted          | Blue-chip, industrial focus     | Low–Moderate  |
| 💱**Foreign Exchange** | **EUR/USD**          | 2 (Euro vs US Dollar)  | Not applicable          | Major currency pair (forex)     | Moderate–High |
| 🪙 **Crypto**            | **BTC/USD**          | 1 (Bitcoin)            | Not applicable          | Cryptocurrency (decentralized)  | Very High     |
| 🥇** Commodities Market** | ** Gold (XAU / USD)** | 1 (Gold)               | Not applicable          | Precious metal & inflation hedge   |  Moderate     |
| 🛢** Commodities Market** | ** Crude Oil (WTI)**  | 1 (Oil)                | Not applicable          | Energy commodity & macro indicator |  High          |


