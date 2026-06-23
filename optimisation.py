import backtrader as bt
from main import load_data
from strategies.tma import TripleMovingAverageStrategy

def run_optimization():
    # ==========================================
    # OPTIMIZATION CONTROL PANEL
    # ==========================================
    TICKER_SYMBOL       = "AAPL"        # Asset to optimize
    START_DATE          = "2015-01-01"  # Historical training window start
    END_DATE            = "2024-01-01"  # Historical training window end
    INITIAL_CASH        = 100000.0      # Virtual starting balance
    COMMISSION_RATE     = 0.001         # 0.1% broker transaction fee
    SLIPPAGE_PERCENT    = 0.0005        # 0.05% price slippage execution
    STAKE_SIZE          = 100           # Shared size per trade
    # ==========================================

    # Initialize Cerebro for optimization
    cerebro = bt.Cerebro(optds=True) # Enables optimization data streaming

    # 1. Load data via the loader function we built in main.py
    market_data = load_data(TICKER_SYMBOL, START_DATE, END_DATE)
    cerebro.adddata(market_data)

    # 2. Set up the Grid Search Parameters
    # Instead of addstrategy(), we use optstrategy() to pass ranges of values to test
    cerebro.optstrategy(
        TripleMovingAverageStrategy,
        short_period=[5, 10, 20],       # 3 options
        medium_period=[50, 100, 150],   # 3 options
        long_period=[200, 250, 300]     # 3 options
    )                                   # Total distinct runs = 3 * 3 * 3 = 27 combinations

    # 3. Configure Broker and Sizer settings
    cerebro.broker.setcash(INITIAL_CASH)
    cerebro.broker.setcommission(commission=COMMISSION_RATE)
    cerebro.broker.set_slippage_perc(SLIPPAGE_PERCENT)
    cerebro.addsizer(bt.sizers.FixedSize, stake=STAKE_SIZE)

    # 4. Add Risk Analyzers (Replaces Task 8's manual math)
    # This automatically computes Sharpe Ratio and Returns under the hood
    cerebro.addanalyzer(bt.analyzers.SharpeRatio, _name='sharpe', annualize=True, riskfreerate=0.0)
    cerebro.addanalyzer(bt.analyzers.Returns, _name='returns')

    print("Executing parallel multi-core grid optimization search...")
    # Run the optimization matrix (maxcpu=1 ensures stability across all operating systems)
    optimization_results = cerebro.run(maxcpu=1)

    # 5. Extract and sort results to find the winner
    compiled_results = []

    # Loop through the results of all 27 runs
    for run in optimization_results:
        strategy_instance = run[0]
        
        # Pull the specific parameter combination used in this run
        p_short  = strategy_instance.params.short_period
        p_medium = strategy_instance.params.medium_period
        p_long   = strategy_instance.params.long_period
        
        # Extract the performance metrics calculated by the analyzers
        final_value  = strategy_instance.broker.getvalue()
        total_return = strategy_instance.analyzers.returns.get_analysis().get('rtot', 0.0)
        
        sharpe_analysis = strategy_instance.analyzers.sharpe.get_analysis()
        sharpe_ratio = sharpe_analysis.get('sharperatio', 0.0)
        # If the strategy took no trades or crashed, Sharpe can return None. Fix it to 0.0
        if sharpe_ratio is None: 
            sharpe_ratio = 0.0

        compiled_results.append({
            'parameters': (p_short, p_medium, p_long),
            'value': final_value,
            'return': total_return,
            'sharpe': sharpe_ratio
        })

    # Sort results by final portfolio value in descending order
    compiled_results.sort(key=lambda x: x['value'], reverse=True)

    # 6. Print the Optimization Dashboard Matrix
    print("\n" + "="*60)
    print("                OPTIMIZATION RESULTS MATRIX LOG               ")
    print("="*60)
    print(f"{'Rank':<5} | {'(Short, Med, Long)':<20} | {'Final Value':<12} | {'Sharpe Ratio':<12}")
    print("-"*60)
    
    for rank, res in enumerate(compiled_results[:5], start=1): # Show top 5 combinations
        param_str = str(res['parameters'])
        print(f"{rank:<5} | {param_str:<20} | {res['value']:<12.2f} | {res['sharpe']:<12.4f}")
    print("="*60)

    winner = compiled_results[0]
    print(f"\n OPTIMIZATION WINNER: Parameters {winner['parameters']} yielded ${winner['value']:.2f}")

if __name__ == "__main__":
    run_optimization()
