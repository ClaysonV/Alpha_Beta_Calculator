import yfinance as yf
import pandas as pd
import statsmodels.api as sm
import numpy as np

def calculate_capm(asset_ticker, market_ticker, rf_ticker, period="5y", interval="1mo"):
    """
    Calculates Alpha and Beta for a given asset relative to a market benchmark
    using the Capital Asset Pricing Model (CAPM).

    Args:
        asset_ticker (str): The ticker symbol for the asset (e.g., 'AAPL').
        market_ticker (str): The ticker symbol for the market (e.g., '^GSPC' for S&P 500).
        rf_ticker (str): The ticker symbol for the risk-free rate (e.g., '^IRX' for 13-week T-bill).
        period (str): The time period for data (e.g., '1y', '5y', 'max').
        interval (str): The data frequency (e.g., '1d', '1wk', '1mo').

    Returns:
        dict: A dictionary containing Alpha (annualized), Beta, and the regression summary.
    """
    print(f"Calculating CAPM for {asset_ticker} vs {market_ticker}...")

    try:
        # --- 1. Fetch Data ---
        # Download historical data for asset, market, and risk-free rate
        all_data = yf.download([asset_ticker, market_ticker, rf_ticker], period=period, interval=interval)
        
        # Check if we have 'Adj Close' (for stocks/ETFs) or 'Close' (for rates)
        # Use 'Adj Close' if available, as it accounts for dividends and splits
        if 'Adj Close' in all_data:
            data = all_data['Adj Close'].dropna()
        else:
            # Fallback for indices or rates that might only have 'Close'
            data = all_data['Close'].dropna()

        if data.empty:
            print("Error: Could not download or process data. Tickers might be incorrect or data unavailable for the period.")
            return None

        # --- 2. Process Data & Calculate Returns ---
        
        # Calculate percentage change for asset and market returns
        # For the risk-free rate ('^IRX'), the value is an annualized percentage yield.
        # We need to convert it to a monthly (or periodic) rate.
        
        returns = pd.DataFrame()
        returns['asset'] = data[asset_ticker].pct_change()
        returns['market'] = data[market_ticker].pct_change()
        
        # Process risk-free rate:
        # The '^IRX' ticker gives an annualized rate (e.g., 5.25 means 5.25%).
        # We need to convert this to the *interval's* rate.
        # Example for '1mo': annual_rate / 12
        # Example for '1d': annual_rate / 252 (trading days)
        # Note: We align the rf rate with the *start* of the period, so we use shift(1)
        
        if interval == '1mo':
            rf_periodic_rate = (data[rf_ticker] / 100) / 12
        elif interval == '1wk':
            rf_periodic_rate = (data[rf_ticker] / 100) / 52
        elif interval == '1d':
            rf_periodic_rate = (data[rf_ticker] / 100) / 252
        else:
            print(f"Warning: Unsupported interval '{interval}' for risk-free rate. Defaulting to 0.")
            rf_periodic_rate = 0

        returns['rf'] = rf_periodic_rate.shift(1) # Use rate from start of period
        
        # Drop the first row (NaN from pct_change) and any rows with missing data
        returns = returns.dropna()

        if returns.empty:
            print("Error: Not enough overlapping data to calculate returns.")
            return None

        # --- 3. Calculate Excess Returns ---
        # This is the core of the regression: R_asset - R_f = alpha + beta * (R_market - R_f)
        returns['asset_excess'] = returns['asset'] - returns['rf']
        returns['market_excess'] = returns['market'] - returns['rf']

        # --- 4. Perform Regression ---
        # Y = Asset's Excess Return
        # X = Market's Excess Return
        Y = returns['asset_excess']
        X = returns['market_excess']

        # Add a constant (intercept) to the X variable
        # This constant represents Alpha
        X_with_const = sm.add_constant(X)

        # Fit the Ordinary Least Squares (OLS) model
        model = sm.OLS(Y, X_with_const).fit()

        # --- 5. Extract Results ---
        # The constant (intercept) is our Alpha for the period
        # The coefficient for the market return is our Beta
        
        # model.params[0] is 'const' (Alpha)
        # model.params[1] is 'market_excess' (Beta)
        alpha_periodic = model.params.iloc[0] 
        beta = model.params.iloc[1]

        # Annualize Alpha
        # (1 + monthly_alpha)^12 - 1
        periods_per_year = {
            '1mo': 12,
            '1wk': 52,
            '1d': 252
        }.get(interval, 1) # Default to 1 (no annualization) if interval is unknown

        alpha_annualized = (1 + alpha_periodic) ** periods_per_year - 1

        return {
            "asset_ticker": asset_ticker,
            "market_ticker": market_ticker,
            "beta": beta,
            "alpha_periodic": alpha_periodic,
            "alpha_annualized": alpha_annualized,
            "rsquared": model.rsquared,
            "summary": model.summary()
        }

    except Exception as e:
        print(f"An error occurred: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    # --- Configuration ---
    ASSET = 'MSFT'      # Stock you want to analyze (e.g., 'AAPL', 'GOOGL', 'TSLA')
    MARKET = '^GSPC'    # Market benchmark (S&P 500)
    RISK_FREE = '^IRX'  # Risk-free rate (13 Week Treasury Bill)
    PERIOD = '5y'       # Data period (e.g., '1y', '5y', '10y')
    INTERVAL = '1mo'    # Data interval ('1d' for daily, '1wk' for weekly, '1mo' for monthly)

    # --- Run Calculation ---
    results = calculate_capm(ASSET, MARKET, RISK_FREE, PERIOD, INTERVAL)

    # --- Display Results ---
    if results:
        print("\n" + "="*50)
        print(f"CAPM Analysis: {results['asset_ticker']} vs {results['market_ticker']}")
        print(f"Period: {PERIOD}, Interval: {INTERVAL}")
        print("="*50)
        
        print(f"\nBeta (β):     {results['beta']:.4f}")
        print(f"Alpha (α):    {results['alpha_annualized']*100:.4f}% (Annualized)")
        print(f"R-squared:    {results['rsquared']:.4f}")

        print("\n--- Interpretation ---")
        print(f"Beta = {results['beta']:.2f}: For every 1% move in the market ({MARKET}), {ASSET} is expected to move {results['beta']:.2f}%.")
        if results['beta'] > 1:
            print(f"   (This indicates {ASSET} is more volatile than the market.)")
        elif results['beta'] < 1:
            print(f"   (This indicates {ASSET} is less volatile than the market.)")
        else:
            print(f"   (This indicates {ASSET} moves in line with the market.)")
            
        print(f"\nAlpha = {results['alpha_annualized']*100:.2f}%: After accounting for market risk (Beta), the asset has")
        if results['alpha_annualized'] > 0:
            print(f"   outperformed its expected return by {results['alpha_annualized']*100:.2f}% per year.")
        elif results['alpha_annualized'] < 0:
             print(f"   underperformed its expected return by {abs(results['alpha_annualized']*100):.2f}% per year.")
        else:
            print("   performed exactly as expected.")
        
        print(f"\nR-squared = {results['rsquared']:.2f}: {results['rsquared']*100:.0f}% of {ASSET}'s price movements are explained by movements in the market ({MARKET}).")

        # Uncomment the line below to see the full statistical summary
        # print(f"\n--- Full Regression Summary ---\n{results['summary']}")