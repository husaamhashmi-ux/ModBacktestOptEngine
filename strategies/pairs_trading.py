import backtrader as bt
import pandas as pd
import numpy as np
from statsmodels.regression.linear_model import OLS
from statsmodels.tools.tools import add_constant

class PairsTradingStrategy(bt.Strategy):
    params = dict(
        zscore_entry=2.0,  # Z-score deviation boundary to open trades
        zscore_exit=0.1,   # Z-score threshold to close trades and lock in mean reversion
        lookback=30        # Rolling window size for the ordinary least squares (OLS) regression
    )

    def __init__(self):
        # Explicit references to the dual historical tracking feeds
        self.stock1 = self.datas[0].close
        self.stock2 = self.datas[1].close

        # Core historical series containers
        self.spread = []
        self.hedge_ratio = None
        self.LS_const = None
        self.order_stock1 = None
        self.order_stock2 = None

    def calculate_hedge_ratio(self, p1, p2):
        """Computes dynamic hedge ratio and intercept constant via linear regression."""
        y = pd.Series(p1)
        x = pd.Series(p2)
        x_with_constant = add_constant(x)
        
        model = OLS(y, x_with_constant).fit()
        
        ls_const = model.params.iloc[0]
        hedge_ratio = model.params.iloc[1]
        return ls_const, hedge_ratio

    def calculate_zscore(self, spread_history):
        """Computes the instantaneous normalized Z-score of the current spread."""
        current_spread = spread_history[-1]
        spread_mean = np.mean(spread_history)
        spread_std = np.std(spread_history)
        
        if spread_std == 0:
            return 0.0
            
        return (current_spread - spread_mean) / spread_std

    def next(self):
        # Wait until engine accumulates enough historical data bars
        if len(self) < self.params.lookback:
            return

        # 1. Generate local historical window arrays
        p1_window = self.stock1.get(size=self.params.lookback)
        p2_window = self.stock2.get(size=self.params.lookback)

        # 2. Extract linear regression parameters dynamically
        self.LS_const, self.hedge_ratio = self.calculate_hedge_ratio(p1_window, p2_window)

        # 3. Process the current tracking spread sequence
        spread_value = self.stock1[0] - (self.hedge_ratio * self.stock2[0]) + self.LS_const
        self.spread.append(spread_value)

        # Enforce rolling execution boundaries on your array window
        if len(self.spread) > self.params.lookback:
            self.spread.pop(0)
            
        if len(self.spread) < self.params.lookback:
            return

        # 4. Calculate tracking statistical metric
        zscore = self.calculate_zscore(self.spread)

        # 5. Handle active cross-execution positions
        size1 = 100
        size2 = int(self.hedge_ratio * 100)

        pos1 = self.getposition(self.datas[0]).size
        pos2 = self.getposition(self.datas[1]).size

        # Execution Logic Matrix
        if pos1 == 0 and pos2 == 0:
            # Spread is widened -> Short Stock 1, Long Stock 2
            if zscore > self.params.zscore_entry:
                self.order_stock1 = self.sell(data=self.datas[0], size=size1)
                self.order_stock2 = self.buy(data=self.datas[1], size=size2)
            # Spread is compressed -> Long Stock 1, Short Stock 2
            elif zscore < -self.params.zscore_entry:
                self.order_stock1 = self.buy(data=self.datas[0], size=size1)
                self.order_stock2 = self.sell(data=self.datas[1], size=size2)
                
        elif pos1 != 0 or pos2 != 0:
            # Mean reversion achieved -> Liquidation exit
            if abs(zscore) < self.params.zscore_exit:
                self.order_stock1 = self.close(data=self.datas[0])
                self.order_stock2 = self.close(data=self.datas[1])
