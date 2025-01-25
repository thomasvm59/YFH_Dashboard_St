import pandas as pd
import logging
from concurrent.futures import ThreadPoolExecutor
import yfinance as yf
from yahooquery import Screener
import datetime
import streamlit as st

# Setup logging
logging.basicConfig(level=logging.INFO)

# Set global float format to display 2 decimal places
pd.options.display.float_format = '{:.2f}'.format

sp500_tickers = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "BRK-B", "JNJ", "V", "NVDA", "WMT",
    "TSLA", "JPM", "PG", "UNH", "HD", "DIS", "PYPL", "MA", "ADBE", "CMCSA",
    "NFLX", "VZ", "KO", "PFE", "PEP", "T", "MRK", "CSCO", "INTC", "XOM",
    "BAC", "ABT", "CVX", "ORCL", "ACN", "CRM", "ABBV", "NKE", "LLY", "COST",
    "TMO", "DHR", "MCD", "MDT", "NEE", "TXN", "PM", "WFC", "BMY", "LIN",
    "RTX", "UNP", "HON", "LOW", "QCOM", "IBM", "INTU", "SBUX", "CAT", "AMGN",
    "GS", "BLK", "DE", "CHTR", "ISRG", "ADP", "AMD", "BKNG", "PLD", "AXP",
    "NOW", "SPGI", "CI", "ZTS", "GE", "AMAT", "SYK", "MMM", "TGT", "CB",
    "LMT", "ADI", "EL", "MO", "AMT", "BA", "FIS", "GILD", "SCHW", "MS", "C",
    # "ETN", "MU", "MDLZ", "USB", "VRTX", "TJX", "PNC", "APD", "CCI", "SHW",
    # "FDX", "KLAC", "WM", "SO", "NSC", "PGR", "EQIX", "DUK", "ICE", "REGN",
    # "PSA", "ITW", "ECL", "ADM", "BDX", "TRV", "HUM", "AON", "COF", "MRNA",
    # "EW", "ATVI", "MCO", "ADSK", "CSX", "MAR", "CMG", "HCA", "ROP", "CTSH",
    # "PRU", "KMB", "AEP", "VRSK", "AZO", "BIIB", "ORLY", "IDXX", "ROST",
    # "CME", "STZ", "A", "FTNT", "PAYX", "SLB", "APH", "MSI", "XEL", "BK",
    # "KMI", "ILMN", "D", "HLT", "MCHP", "MPC", "DXCM", "WTW", "DOW", "EBAY",
    # "WBA", "SPG", "SYY", "HPQ", "NEM", "GPN", "ALL", "PXD", "DD", "CNC",
    # "IQV", "LRCX", "TFC", "MET", "PSX", "PPG", "ALB", "NOC", "EA", "DAL",
    # "FAST", "RSG", "PH", "DFS", "TEL", "F", "WMB", "NTRS", "ZBH", "BAX",
    # "VLO", "HES", "KR", "PCAR", "CHD", "MTD", "CF", "KEYS", "LEN", "EQR",
    # "OXY", "EXC", "EIX", "BKR", "FE", "ESS", "HIG", "WEC", "ATO", "DTE",
    # "ETR", "PEG", "CMS", "AES", "LHX", "NDAQ", "IRM", "HOLX", "SBAC", "XYL",
    # "DLTR", "MKC", "TSN", "DRI", "LUV", "STT", "FITB", "HBAN", "AFL", "AIG",
    # "DHI", "CAG", "CHRW", "EXPE", "VTR", "PPL", "MTB", "NVR", "RMD", "HII",
    # "COO", "CARR", "HSIC", "IPG", "VFC", "ZBRA", "PKI", "XRAY", "CPRT",
    # "TRGP", "FDS", "ZION", "NRG", "FRC", "APA", "VIAC", "GNRC", "AKAM",
    # "CNP", "DVA", "SIVB", "NI", "WYNN", "UAL", "PNR", "NWL", "K", "ETFC",
    # "BXP", "WRK", "WHR", "AAP", "HPE", "SEE", "NLSN", "RL", "MOS", "LYB",
    # "LUMN", "IP", "FTI", "DXC", "ALK", "LEG", "UHS", "CFX", "BBWI", "NWSA",
    # "DISCK", "KIM", "HAS", "NLOK", "VIAC"
]

etf_tickers = ["SPY", "QQQ", "DIA", "IWM"]  # Example ETFs
crypto_tickers = ["BTC-USD", "ETH-USD","XRP-USD","SOL-USD","BNB-USD","DOGE-USD","ADA-USD","TRX-USD","LINK-USD","AVAX-USD"]  # Example cryptocurrencies

def fetch_most_active_tickers():
    screener = Screener()
    # Use the 'most_actives' screener to get the most active tickers
    data = screener.get_screeners('most_actives', count=50)
    results = data['most_actives']['quotes']
    tickers = [item['symbol'] for item in results]
    return tickers


# Function to fetch fundamental data
def fetch_fundamental_data_yahoo(tickers, crypto_tickers, etf_tickers, max_workers=10):
    """
    Fetch fundamental data for a list of tickers using Yahoo Finance API.
    Args:
        tickers (list): List of tickers to fetch data for.
        crypto_tickers (list): List of cryptocurrency tickers.
        etf_tickers (list): List of ETF tickers.
        max_workers (int): Maximum number of threads for parallel processing.
    Returns:
        dict: Dictionary with ticker as key and fundamental data as value.
    """
    fundamentals = {}

    def fetch_ticker_data(ticker):
        # Determine default sector
        if ticker in crypto_tickers:
            default_sector = 'crypto'
        elif ticker in etf_tickers:
            default_sector = 'etf'
        else:
            default_sector = "N/A"

        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return {
                "Sector": info.get("sector", default_sector),
                "PE Ratio": info.get("trailingPE", None),
                "Revenue(Bn)": info.get("totalRevenue", None) / 1_000_000_000 if info.get("totalRevenue") else None,
                "dividendYield": info.get("dividendYield", None),
                "fiveYearAvgDividendYield": info.get("fiveYearAvgDividendYield", None),
                "payoutRatio": info.get("payoutRatio", None),
                "beta": info.get("beta", None),
                "trailingPE": info.get("trailingPE", None),
                "forwardPE": info.get("forwardPE", None),
                "volume(mil)": info.get("volume", None) / 1_000_000 if info.get("volume") else None,
                "averageVolume(mil)": info.get("averageVolume", None) / 1_000_000 if info.get("averageVolume") else None,
                "marketCap(Bn)": info.get("marketCap", None) / 1_000_000_000 if info.get("marketCap") else None,
                "shortPercentOfFloat": info.get("shortPercentOfFloat", None),
                "bookValue": info.get("bookValue", None),
                "trailingEps": info.get("trailingEps", None),
                "forwardEps": info.get("forwardEps", None),
                "symbol": info.get("symbol", None),
                "shortName": info.get("shortName", None),
                "debtToEquity": info.get("debtToEquity", None)
            }
        except Exception as e:
            print(f"Error fetching data for {ticker}: {e}")
            return {"Sector": default_sector, "PE Ratio": None, "Revenue(Bn)": None}

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = executor.map(fetch_ticker_data, tickers)

    # Combine results into a dictionary
    fundamentals = {ticker: result for ticker, result in zip(tickers, results)}

    return fundamentals

@st.cache #to check how to change for @st.cache_data or @st.cache_ressources
def get_data():
    most_active_tickers = fetch_most_active_tickers()
    memes_tickers = [s for s in most_active_tickers if s not in sp500_tickers]
    all_tickers = sp500_tickers + etf_tickers + crypto_tickers + memes_tickers

    # Fetch historical prices
    start_date = "2010-01-01"
    data = yf.download(all_tickers, start=start_date)
    prices = data["Close"].ffill()  # Use adjusted close prices
    prices = prices[lambda x : x.index<datetime.date.today().isoformat()]
    
    # Fetch and process fundamental data
    fundamental_data = fetch_fundamental_data_yahoo(
        tickers=all_tickers,
        crypto_tickers=crypto_tickers,
        etf_tickers=etf_tickers,
        max_workers=10
    )
    
    # Create a DataFrame for fundamentals
    fundamentals = pd.DataFrame.from_dict(fundamental_data, orient="index")
    
    # Create summary table
    summary = pd.DataFrame({
        "last_price": prices.iloc[-1],
        "price_1_d": prices.iloc[-2],
        "price_1_w": prices.iloc[-8],
        "price_1_m": prices.iloc[-31],
        "price_1_y": prices.iloc[-366],
        "ATH Price": prices.max(),
        "1Y_H": prices.iloc[-365:].max(),
        "1Y_L": prices.iloc[-365:].min(),
    })
    
    # Merge summary with fundamentals
    summary = summary.merge(fundamentals, left_index=True, right_index=True)
    
    # Save results to a CSV
    summary.to_csv("market_data_summary.csv")
    
    print("Market data summary saved to 'market_data_summary.csv'.")
    summary['1d_return']=summary['last_price']/summary['price_1_d']-1
    summary['1w_return']=summary['last_price']/summary['price_1_w']-1
    summary['1m_return']=summary['last_price']/summary['price_1_m']-1
    summary['1y_return']=summary['last_price']/summary['price_1_y']-1
    summary['dist_ath']=summary['last_price']/summary['ATH Price']-1
    
    return prices, summary
    

