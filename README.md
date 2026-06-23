# Modular Algorithmic Backtesting & Optimization Engine
# Multi-Strategy Algorithmic Backtesting & Parallel Optimization Engine

A production-grade quantitative research framework built on top of the **Backtrader** ecosystem. This engine enables the rapid prototyping, evaluation, and parallel parameter optimization of systematic trading strategies across multiple asset pipelines.

## Core Architecture Features
* **Modular Multi-Strategy Layout:** Complete separation of concerns. Trading logic, analytical ingestion, and parallel optimization exist in independent, decoupled modules.
* **Dynamic Execution Pipelines:** Features an automated string routing engine capable of handling single-asset pipelines (Trend Following / Volatility Breakouts) and dual-asset feeds simultaneously.
* **Parallel Grid Optimization:** Leverages multi-core processing to evaluate parameter matrices dynamically, tracking performance metrics via industrial-grade risk analyzers.

---

## Implemented Algorithmic Modules

### 1. Trend Following: Triple Moving Average (TMA)
* **Logic:** Employs structural macro alignment across Three Simple Moving Averages (Short, Medium, Long) to capture programmatic trend expansion.
* **Risk Mitigation:** Managed via automated trailing stop-losses ($2.0\%$) to systematically preserve capital.

### 2. Volatility Mean Reversion: Bollinger Bands Breakout
* **Logic:** Exploits historical price distributions by tracking standard deviation volatility bands ($\pm 3\sigma$) around a lookback baseline. 
* **Execution:** Opens mean-reversion positions at statistical extremes (oversold/overbought) and liquidates positions once price returns to the moving average baseline.

### 3. Statistical Arbitrage: Cointegrated Pairs Trading
* **Logic:** A market-neutral strategy utilizing Ordinary Least Squares (OLS) regression to dynamically map the hedge ratio ($\beta$) and intercept constant between two fundamentally cointegrated corporate assets (e.g., $PEP$ vs. $KO$).
* **Mathematical Framework:** Computes a rolling Z-Score tracking spread deviations from historical equilibrium, opening paired long/short tracking legs when $|Z| > 2.0$.

$$\text{Spread} = \text{Price}_{\text{Asset 1}} - (\beta \times \text{Price}_{\text{Asset 2}}) + \text{Constant}$$

$$Z\text{-Score} = \frac{\text{Spread} - \mu_{\text{Spread}}}{\sigma_{\text{Spread}}}$$

---

## Installation & Getting Started

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git](https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git)
   cd YOUR_REPO_NAME
