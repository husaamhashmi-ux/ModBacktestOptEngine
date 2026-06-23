import backtrader as bt
import yfinance as yf
import pandas as pd
from strategies.tma import TripleMovingAverageStrategy
from strategies.bollinger import BollingerBandsStrategy
from strategies.pairs_trading import PairsTradingStrategy

def load_data(ticker_symbol, start_date, end_date):
    """Downloads trading data from yfinance and formats it for Backtrader."""
    print(f"Downloading historical data for {ticker_symbol}...")
    df = yf.download(ticker_symbol, start=start_date, end=end_date, auto_adjust=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    if 'Adj Close' in df.columns and not df['Adj Close'].isnull().all():
        df['Adj Close'] = df['Adj Close'].fillna(df['Close'])
        close_column = 'Adj Close'
    else:
        close_column = 'Close'

    df = df[['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume']]

    data = bt.feeds.PandasData(
        dataname=df,
        datetime=None, 
        open='Open',
        high='High',
        low='Low',
        close=close_column,
        volume='Volume',
        openinterest=-1
    )
    return data

def run_backtest():
    # ==========================================
    # USER CONTROL PANEL
    # ==========================================
    STRATEGY_CHOICE     = "PAIRS"      # Options: "TMA", "BOLLINGER", or "PAIRS"
    
    # Single Ticker Asset Configuration (Used for TMA & BOLLINGER)
    TICKER_SINGLE       = "AAPL"       
    
    # Cointegrated Multi-Asset Configuration (Used for PAIRS trading only)
    TICKER_PAIR_1       = "PEP"        # PepsiCo Inc.
    TICKER_PAIR_2       = "KO"         # The Coca-Cola Company
    
    START_DATE          = "2015-01-01" 
    END_DATE            = "2024-01-01" 
    INITIAL_CASH        = 1000000.0    # Set to £1M for portfolio pairing depth
    COMMISSION_RATE     = 0.001        # 0.1% transaction cost
    SLIPPAGE_PERCENT    = 0.0005       # 0.05% execution price safety margin
    # ==========================================

    cerebro = bt.Cerebro()

    # 1. Dynamically add data streams based on selection
    if STRATEGY_CHOICE.upper() == "PAIRS":
        print(f"Initializing Statistical Arbitrage: Pairing {TICKER_PAIR_1} and {TICKER_PAIR_2}...")
        
        # Load asset data feeds independently
        data1 = load_data(TICKER_PAIR_1, START_DATE, END_DATE)
        data2 = load_data(TICKER_PAIR_2, START_DATE, END_DATE)
        
        # Add both to cerebro (order matters: data0=PEP, data1=KO)
        cerebro.adddata(data1)
        cerebro.adddata(data2)
        
        cerebro.addstrategy(PairsTradingStrategy)
        
    else:
        # Standard Single Asset Ingestion Pipeline
        market_data = load_data(TICKER_SINGLE, START_DATE, END_DATE)
        cerebro.adddata(market_data)
        
        if STRATEGY_CHOICE.upper() == "TMA":
            print("Initializing Strategy: Triple Moving Average...")
            cerebro.addstrategy(TripleMovingAverageStrategy)
        elif STRATEGY_CHOICE.upper() == "BOLLINGER":
            print("Initializing Strategy: Bollinger Bands...")
            cerebro.addstrategy(BollingerBandsStrategy)
        else:
            raise ValueError(f"Unknown strategy code mapping: '{STRATEGY_CHOICE}'")

    # 2. Virtual Broker Integration Options
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.broker.setcommission(commission=COMMISSION_RATE)
    cerebro.broker.set_slippage_perc(SLIPPAGE_PERCENT)
    
    # We do not use a global fixed sizer for pairs because sizes vary by the hedge ratio inside the strategy file!

    print(f"Starting Portfolio Value: {cerebro.broker.getvalue():.2f}")
    cerebro.run()
    print(f"Final Portfolio Value: {cerebro.broker.getvalue():.2f}")

if __name__ == "__main__":
    run_backtest()
