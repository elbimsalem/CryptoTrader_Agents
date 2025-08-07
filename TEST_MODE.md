# 🧪 Test Mode: Extended Autonomous Trading Simulation

Test Mode provides **comprehensive portfolio simulation** with virtual trading, performance tracking, and daily reporting to evaluate trading strategies over extended periods **without real money risk**.

## 🎯 **Key Features**

- **💰 Virtual Portfolio**: Start with configurable initial balance (default $10,000)
- **🤖 14 Specialized Agents**: Complete autonomous trading + simulation agents
- **📊 Real-time Tracking**: Live portfolio value, P&L, and position monitoring  
- **📈 Daily Reports**: Automated performance summaries with insights
- **🔗 Token Optimization**: Intelligent scheduling to minimize costs
- **📋 Comprehensive Logging**: Complete audit trail of all decisions and trades
- **⏰ Extended Duration**: Run simulations for days/weeks/months
- **📊 Benchmark Comparison**: Performance vs market indices

---

## 🚀 **Quick Start**

### **Option 1: Interactive Runner** (Recommended)
```bash
python run_test_mode.py
```

### **Option 2: Command Line**
```bash
PYTHONPATH=src python -m crypto_trader.test_mode_main \
    --initial-balance 10000 \
    --duration-days 7 \
    --max-tokens 150000
```

### **Option 3: Custom Configuration**
```bash
PYTHONPATH=src python -m crypto_trader.test_mode_main \
    --initial-balance 25000 \
    --duration-days 30 \
    --max-tokens 200000 \
    --quick-interval 20 \
    --medium-interval 90 \
    --volatility-threshold 0.02 \
    --reset-portfolio
```

---

## 🤖 **14-Agent System Architecture**

### **Core Trading Agents (10)**
1. **Market Scanner** - Identifies trading opportunities
2. **Asset Selector** - Chooses optimal cryptocurrencies  
3. **Market Data Analyst** - Technical analysis and indicators
4. **News & Sentiment Researcher** - Market intelligence gathering
5. **Crypto Analyst** - Comprehensive fundamental analysis
6. **Risk Manager** - Position sizing and risk controls
7. **Portfolio Manager** - Allocation optimization
8. **Trade Executor** - Virtual trade execution
9. **Performance Monitor** - Real-time tracking
10. **Strategy Coordinator** - Master decision making

### **Test Mode Specialists (4)**
11. **Portfolio Simulator** - Virtual trading execution
12. **Trade Logger** - Comprehensive audit trails
13. **Daily Reporter** - Performance analysis and insights
14. **Market Benchmark** - Comparative performance analysis

---

## 📊 **Portfolio Simulation Features**

### **Virtual Trading Engine**
- **Realistic Fees**: 0.1% trading fee simulation
- **Position Limits**: Maximum 5 concurrent positions
- **Risk Controls**: 30% max allocation per asset, $100 minimum position
- **Balance Tracking**: Real-time cash and position values
- **Trade History**: Complete execution logs with timestamps

### **Performance Tracking**
- **Real-time P&L**: Unrealized and realized gains/losses
- **Portfolio Value**: Combined cash + position values
- **Daily Returns**: Day-over-day performance analysis
- **Cumulative Returns**: Total performance since inception
- **Risk Metrics**: Volatility, drawdown, Sharpe ratio

### **Position Management**
- **Multi-asset Support**: Hold up to 5 cryptocurrencies simultaneously
- **Dynamic Rebalancing**: Automatic allocation adjustments
- **Stop Loss Simulation**: Risk management rule enforcement
- **Portfolio Correlation**: Diversification effectiveness tracking

---

## 📈 **Daily Reporting System**

Each day generates a comprehensive performance report:

### **Executive Summary**
- Portfolio value change ($ and %)
- Best/worst performing assets
- Trading activity summary
- Key decisions and actions

### **Performance Analysis**
- Daily P&L breakdown
- Cumulative returns vs benchmarks
- Risk-adjusted performance metrics
- Volatility and drawdown analysis

### **Trading Review**
- Trades executed with rationale
- Success rate and win/loss analysis
- Market timing effectiveness
- Risk management adherence

### **Strategic Recommendations**
- Portfolio optimization opportunities
- Strategy refinement suggestions
- Risk management improvements
- Next-day focus areas

---

## 💰 **Token Usage & Optimization**

### **Smart Scheduling Integration**
Test Mode uses the intelligent scheduler to optimize token usage:

| Analysis Level | Frequency | Tokens | Description |
|---------------|-----------|--------|-------------|
| **Monitor** | 5 min | 0 | Portfolio tracking only |
| **Quick Scan** | 30 min | ~5K | Light analysis (2-3 agents) |
| **Medium Analysis** | 2 hours | ~15K | Moderate analysis (5-7 agents) |
| **Full Analysis** | 6 hours | ~35K | Complete analysis (all 14 agents) |

### **Budget Recommendations**

#### **Conservative (~$15-20/day)**
- **100,000 tokens/day**
- Focus on major market moves
- Full analysis 1-2x daily
- Ideal for learning and testing

#### **Moderate (~$20-30/day)**  
- **150,000 tokens/day**
- Balanced monitoring and analysis
- Responsive to market volatility
- **Recommended for most users**

#### **Aggressive (~$30-50/day)**
- **250,000 tokens/day**
- High-frequency analysis
- Maximum market responsiveness
- For intensive strategy testing

---

## 📊 **Sample Daily Report**

```
📊 DAILY PERFORMANCE REPORT - 2025-08-07
═══════════════════════════════════════════

💰 PORTFOLIO SUMMARY:
   Starting Value: $10,250.00
   Ending Value:   $10,487.50
   Daily P&L:      +$237.50 (+2.32%)
   Total P&L:      +$487.50 (+4.87%)

📈 POSITIONS (3 active):
   • ETHUSDT: $4,200.00 (+3.45%) - Top Performer
   • SOLUSDT: $3,150.00 (+1.82%)  
   • BTCUSDT: $2,100.00 (-0.95%) - Needs Review

⚡ TRADING ACTIVITY:
   • 09:30 - BUY 0.0245 BTC @ $42,857 (Risk: volatility breakout)
   • 14:15 - SELL 1.25 SOL @ $168.40 (Profit taking: +8.2%)
   • 16:45 - BUY 0.85 ETH @ $3,705 (DCA strategy)

🎯 KEY INSIGHTS:
   • Ethereum showing strong momentum (+3.45%)
   • Portfolio allocation within risk limits
   • Market volatility increasing - consider reducing position sizes
   • Bitcoin correlation breakdown detected

📊 RECOMMENDATIONS:
   1. Consider taking partial profits on ETH position
   2. Monitor BTC correlation for rebalancing opportunity  
   3. Maintain cash buffer (currently 18.5%)
   4. Watch for volume surge in SOL for re-entry

🏆 BENCHMARK COMPARISON:
   Strategy: +2.32% | BTC: +0.52% | ETH: +1.78% | Market: +1.24%
   ✅ Outperforming all benchmarks today
```

---

## 🔧 **Configuration Options**

### **Portfolio Settings**
```bash
--initial-balance 10000      # Starting USD amount
--duration-days 7           # Simulation length
--reset-portfolio           # Start fresh
```

### **Token Management**
```bash
--max-tokens 150000         # Daily token limit
```

### **Analysis Frequency**
```bash
--monitor-interval 5        # Monitor frequency (minutes)
--quick-interval 30         # Quick scan interval
--medium-interval 120       # Medium analysis interval  
--full-interval 360         # Full analysis interval
```

### **Market Sensitivity**
```bash
--volatility-threshold 0.03 # Volatility trigger level
--volume-threshold 0.25     # Volume surge threshold
```

---

## 📋 **Generated Files**

Test Mode creates comprehensive documentation:

### **Real-time Files**
- **`test_mode.log`** - Complete execution log
- **`test_mode_portfolio.json`** - Current portfolio state
- **`test_mode_trades.json`** - All trade executions
- **`test_mode_reports.json`** - Daily performance reports

### **Final Reports**
- **`test_simulation_final_report_YYYYMMDD_HHMMSS.json`** - Complete simulation summary
- **Daily markdown reports** - Human-readable performance summaries

---

## 🎯 **Use Cases**

### **Strategy Development**
- Test new trading algorithms safely
- Optimize risk management parameters
- Evaluate market timing effectiveness
- Compare different allocation strategies

### **Education & Learning**
- Understand autonomous trading behavior
- Learn from AI decision-making process
- Practice portfolio management concepts
- Observe market correlation effects

### **Performance Validation**
- Backtest strategies with live market data
- Compare against benchmark performance
- Measure risk-adjusted returns
- Validate trading hypothesis

### **Long-term Studies**
- Multi-week/month simulations
- Market regime adaptation analysis
- Drawdown and recovery patterns
- Strategy robustness testing

---

## ⚡ **Performance Tips**

1. **Start Conservative**: Begin with lower token budgets to understand patterns
2. **Monitor Daily Reports**: Review performance summaries for insights
3. **Adjust Thresholds**: Fine-tune volatility/volume triggers based on results
4. **Extended Runs**: Longer simulations provide more meaningful statistics
5. **Compare Benchmarks**: Use performance comparisons to validate effectiveness

---

## 🚦 **Status Monitoring**

Real-time status indicators during simulation:

- **🟢 Monitoring**: Portfolio tracking active
- **🟡 Quick Analysis**: Light AI analysis running
- **🟠 Medium Analysis**: Moderate AI analysis running  
- **🔴 Full Analysis**: Complete 14-agent analysis running
- **🔥 Market Alert**: High volatility/volume detected
- **💰 Token Warning**: Approaching daily limits
- **📊 Daily Report**: Performance summary generated

---

## 🛡️ **Safety Features**

- **Virtual Money Only**: No real trading or financial risk
- **Token Limits**: Hard daily caps prevent overspending
- **Error Recovery**: Graceful handling of API failures
- **State Persistence**: Resume simulations after interruption
- **Comprehensive Logging**: Complete audit trail for analysis
- **Performance Bounds**: Realistic simulation constraints

---

## 📞 **Support & Troubleshooting**

### **Common Issues**
- **"Portfolio not found"**: Use `--reset-portfolio` flag
- **"Token limit exceeded"**: Increase `--max-tokens` or wait for daily reset
- **"Analysis failed"**: Check `test_mode.log` for detailed errors

### **Optimization**
- **Slow performance**: Reduce analysis frequency intervals
- **High token usage**: Increase thresholds to reduce triggers
- **Poor results**: Review daily reports for strategy insights

---

**Ready to Test Your Trading Strategies? 🚀📈**

Start with: `python run_test_mode.py`