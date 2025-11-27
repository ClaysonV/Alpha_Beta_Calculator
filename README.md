# CAPM Alpha & Beta Calculator

This Python script calculates the **Alpha (α)** and **Beta (β)** of a financial asset relative to a market benchmark using the **Capital Asset Pricing Model (CAPM)**. It downloads historical data from Yahoo Finance using `yfinance` and performs an OLS regression using `statsmodels`.

---

##  What Is This and Why Is It Used?
This tool applies the Capital Asset Pricing Model, a core concept in finance that measures how much of an asset’s return is due to market risk. CAPM helps investors answer two major questions:

1. **How risky is an investment compared to the market?**  
   This is measured by **Beta (β)**. A high beta means the asset is more volatile than the market, while a lower beta means it is more stable.

2. **Is the asset performing better or worse than expected after adjusting for risk?**  
   This is measured by **Alpha (α)**. If alpha is positive, the asset delivered more return than the market would predict given its level of risk. If negative, the asset underperformed.

Investors, analysts, funds, and quants use CAPM to:
- Evaluate whether a stock is worth investing in  
- Compare performance across different securities  
- Measure risk-adjusted returns  
- Understand how much of a stock’s movement is caused by the overall market

This script automates all of that using real market data.


##  What the Script Does

The script fits the CAPM equation:

(R_a - R_f) = α + β(R_m - R_f) + ε

**Where:**

- \( R_a \) – Asset return  
- \( R_m \) – Market return  
- \( R_f \) – Risk-free rate  
- Alpha (α) – risk-adjusted performance  
- Beta (β) – systematic market risk

The program returns:

- **Beta (β)** – volatility relative to the market  
- **Annualized Alpha (α)** – performance above CAPM  
- **R-squared** – how much market movement explains asset movement  
- Data is pulled automatically with Yahoo Finance

---

##  Features

- Computes:
  - Beta (β)
  - Annualized Alpha (α)
  - R-squared
- Uses OLS regression
- Pulls asset, market, and risk-free data automatically
- User-configurable settings

---

## Requirements & Installation

Install dependencies:

```bash
pip install pandas yfinance statsmodels numpy
```
## How to Use
1️ Save the script as:
```bash
capm_calculator.py
```
2️⃣ Open the file and configure settings:
```bash
if __name__ == "__main__":
    ASSET = 'MSFT'      # Asset to analyze
    MARKET = '^GSPC'    # S&P 500
    RISK_FREE = '^IRX'  # 13-Week Treasury Bill
    PERIOD = '5y'       # Time range
    INTERVAL = '1mo'    # Data frequency

    results = calculate_capm(ASSET, MARKET, RISK_FREE, PERIOD, INTERVAL)
```
3️⃣ Run:
```bash
python capm_calculator.py
```
## Example output
```bash
Calculating CAPM for MSFT vs ^GSPC...
[*********************100%%**********************]  3 of 3 completed

CAPM Analysis: MSFT vs ^GSPC
Period: 5y, Interval: 1mo

Beta (β):     1.0850
Alpha (α):    9.8142% (Annualized)
R-squared:    0.7380

## Interpreting Metrics
Beta (β) — Systematic Risk
--------------------------
β > 1 : More volatile than the market  
β < 1 : Less volatile  
β = 1 : Moves with the market


Alpha (α) — Risk-Adjusted Performance
-------------------------------------
α > 0 : Outperformed expected returns  
α < 0 : Underperformed expected returns


R-Squared
---------
High (e.g., 0.85+) : Market explains price movement well  
Low (e.g., 0.20)   : Market does not explain most price movement
```
