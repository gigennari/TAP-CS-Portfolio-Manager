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

## Home Broket 

## News 

### 📊 Market Indices Banner  

| Market Type          | Index / Pair         | Number of Constituents | Weighting Method        | Sector / Asset Focus            | Volatility    |
| -------------------- | -------------------- | ---------------------- | ----------------------- | ------------------------------- | ------------- |
| 📈 **US Stock Market**  | **NASDAQ Composite** | 3,000+                 | Market-cap weighted     | Tech-heavy (growth & biotech)   | High          |
| 📈 **US Stock Market**  | **S\&P 500**         | 500                    | Market-cap (free-float) | Broad multi-sector (11 sectors) | Moderate      |
| 📈 **US Stock Market**  | **Dow Jones (DJIA)** | 30                     | Price-weighted          | Blue-chip, industrial focus     | Low–Moderate  |
| 💱**Foreign Exchange** | **EUR/USD**          | 2 (Euro vs US Dollar)  | Not applicable          | Major currency pair (forex)     | Moderate–High |
| 🪙 **Crypto**            | **BTC/USD**          | 1 (Bitcoin)            | Not applicable          | Cryptocurrency (decentralized)  | Very High     |
| 🥇** Commodities Market** | ** Gold (XAU / USD)** | 1 (Gold)               | Not applicable          | Precious metal & inflation hedge   |  Moderate     |
| 🛢** Commodities Market** | ** Crude Oil (WTI)**  | 1 (Oil)                | Not applicable          | Energy commodity & macro indicator |  High          |


