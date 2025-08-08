# Trading Modes Configuration

The autonomous trading system now supports **configurable trading modes** that allow you to switch between virtual (paper trading) and real trading seamlessly.

## 🎯 Available Modes

### 1. **Virtual Trading Mode (Paper Trading)**
- ✅ **Safe testing** with virtual money
- ✅ **Portfolio simulation** with realistic fees
- ✅ **Risk-free strategy validation**
- ✅ **Complete audit trails**

### 2. **Real Trading Mode**
- ⚠️  **Live trading** with real money
- ⚠️  **Actual market execution**
- ⚠️  **Real profits and losses**
- ⚠️  **Requires API credentials**

### 3. **Extended Test Mode**
- ✅ **Virtual trading** + comprehensive reporting
- ✅ **Daily performance reports**
- ✅ **Benchmark comparisons**
- ✅ **Multi-agent simulation**

## 🚀 Usage Examples

### Virtual Trading (Paper Trading)
```python
from crypto_trader.autonomous_crew import AutonomousCryptoTradingCrew
from crypto_trader.portfolio_simulator import PortfolioSimulator

# Create portfolio simulator
portfolio_sim = PortfolioSimulator(initial_balance=10000.0)

# Create crew in virtual mode
crew = AutonomousCryptoTradingCrew(
    verbose=True,
    paper_trading=True,  # Enable virtual trading
    portfolio_simulator=portfolio_sim
)

# The trade executor will automatically use Portfolio Simulator Tool
```

### Real Trading (Live Trading)
```python
from crypto_trader.autonomous_crew import AutonomousCryptoTradingCrew

# ⚠️ WARNING: This executes real trades with real money!
crew = AutonomousCryptoTradingCrew(
    verbose=True,
    paper_trading=False,  # Enable real trading
    portfolio_simulator=None  # No simulator needed
)

# The trade executor will automatically use Binance Direct API Tool
# Make sure you have valid BINANCE_API_KEY and BINANCE_API_SECRET in .env
```

### Extended Test Mode
```python
from crypto_trader.test_mode_crew import TestModeCryptoTradingCrew

# Complete test environment with reporting
test_crew = TestModeCryptoTradingCrew(
    initial_balance=10000.0,
    verbose=True
)

# Includes virtual trading + comprehensive reporting agents
```

## 🔧 Configuration Details

### Trade Executor Behavior

| Mode | Agent Role | Tools Used | Purpose |
|------|------------|------------|---------|
| `paper_trading=True` | Virtual Trade Execution Specialist | Portfolio Simulator Tool | Safe testing |
| `paper_trading=False` | Autonomous Trade Execution Specialist | Binance Direct API Tool | Live trading |

### Required Environment Variables

#### For Virtual Trading:
```bash
# LLM Configuration (required)
OPENAI_API_KEY=your_ionos_jwt_token
IONOS_BASE_URL=https://openai.inference.de-txl.ionos.com/v1

# Optional: Search capabilities
SERPER_API_KEY=your_serper_key
```

#### For Real Trading:
```bash
# LLM Configuration (required)
OPENAI_API_KEY=your_ionos_jwt_token
IONOS_BASE_URL=https://openai.inference.de-txl.ionos.com/v1

# Binance API (required for real trading)
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# Optional: Search capabilities
SERPER_API_KEY=your_serper_key
```

## 🏃‍♂️ Quick Start Scripts

### Test Virtual Trading
```bash
python test_trading_modes.py
```

### Run Virtual Trading Session
```bash
python run_test_mode.py
```

### Run Real Trading Session (⚠️ CAUTION)
```bash
python run_real_trading.py
```

## ⚠️ Safety Considerations

### Before Real Trading:
1. ✅ **Test thoroughly** in virtual mode first
2. ✅ **Verify API credentials** are correct
3. ✅ **Start with small amounts**
4. ✅ **Monitor actively** during execution
5. ✅ **Have stop-loss strategy**
6. ✅ **Understand risk tolerance**

### Risk Management:
- The system includes built-in risk management constraints
- Maximum position sizes and portfolio allocation limits
- Stop-loss and take-profit mechanisms
- Regular performance monitoring

## 🎯 Mode Switching

You can easily switch between modes by changing the `paper_trading` parameter:

```python
# For development and testing
crew = AutonomousCryptoTradingCrew(paper_trading=True, ...)

# For production (after thorough testing)
crew = AutonomousCryptoTradingCrew(paper_trading=False, ...)
```

The system automatically configures the appropriate tools and agents based on this setting.

---

**Remember**: Always start with virtual trading to validate strategies before risking real money!