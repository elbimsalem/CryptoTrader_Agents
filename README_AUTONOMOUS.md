# 🤖 Autonomous Cryptocurrency Trading System

An advanced AI-powered autonomous cryptocurrency trading system built with CrewAI and powered by IONOS Cloud models. This system can automatically discover trading opportunities, manage risk, and execute trades across multiple cryptocurrency assets.

## 🚀 Key Features

### ✨ Autonomous Capabilities
- **🔍 Market Discovery**: Automatically scans and identifies profitable trading opportunities
- **📊 Multi-Asset Trading**: Manages multiple cryptocurrency positions simultaneously  
- **🎯 Smart Asset Selection**: Uses AI to select optimal assets based on technical and fundamental analysis
- **⚖️ Advanced Risk Management**: Real-time portfolio risk monitoring and position sizing
- **🔄 Automated Execution**: Direct Binance API integration for trade execution
- **📈 Performance Monitoring**: Continuous performance tracking and optimization

### 🧠 AI-Powered Agents (10 Specialists)
1. **Market Scanner** - Discovers trading opportunities
2. **Asset Selector** - Chooses optimal assets for trading
3. **Market Data Analyst** - Processes real-time market data
4. **News & Sentiment Researcher** - Analyzes market sentiment and news
5. **Crypto Analyst** - Performs comprehensive technical analysis
6. **Risk Manager** - Manages portfolio risk and position sizing
7. **Portfolio Manager** - Optimizes multi-asset allocation
8. **Trade Executor** - Executes trades with optimal timing
9. **Performance Monitor** - Tracks and optimizes performance
10. **Strategy Coordinator** - Orchestrates the entire operation

### ⚡ IONOS Cloud Integration
Optimized model assignments for maximum performance:

| Agent | IONOS Model | Purpose |
|-------|-------------|---------|
| Market Scanner | `mistralai/Mixtral-8x7B-Instruct-v0.1` | Fast data processing |
| Asset Selector | `meta-llama/Llama-3.3-70B-Instruct` | Balanced reasoning |
| Market Data Analyst | `mistralai/Mistral-Nemo-Instruct-2407` | Efficient analysis |
| News Researcher | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | Complex NLP |
| Crypto Analyst | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | Deep analysis |
| Risk Manager | `meta-llama/Llama-3.3-70B-Instruct` | Precise calculations |
| Portfolio Manager | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | Complex optimization |
| Trade Executor | `meta-llama/CodeLlama-13b-Instruct-hf` | Code execution |
| Performance Monitor | `mistralai/Mistral-Small-24B-Instruct` | Fast monitoring |
| Strategy Coordinator | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | Strategic decisions |

## 📋 Prerequisites

- Python 3.10 or higher (< 3.13)
- IONOS Cloud account with AI Hub access
- Binance account (for live trading)
- UV or pip for dependency management

## ⚙️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/edofransisco011/CryptoTrader_Agents.git
   cd CryptoTrader_Agents
   ```

2. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync
   
   # Or using pip
   pip install -e .
   ```

3. **Configure environment**
   ```bash
   # Copy and edit environment file
   cp .env.example .env
   # Edit .env with your API keys
   ```

## 🔑 API Configuration

### Required (Minimum Setup)
```bash
# IONOS Cloud (Required)
OPENAI_API_KEY=your_ionos_jwt_token_here
IONOS_BASE_URL=https://openai.inference.de-txl.ionos.com/v1

# News Research (Recommended)
SERPER_API_KEY=your_serper_api_key_here
```

### For Live Trading
```bash
# Binance API (Required for live trading)
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_api_secret_here
```

### Getting API Keys

1. **IONOS Cloud**: Get JWT token from [IONOS Cloud AI Hub](https://cloud.ionos.com/)
2. **Binance**: Create API key at [Binance API Management](https://www.binance.com/en/my/settings/api-management)
3. **Serper**: Get API key from [Serper.dev](https://serper.dev/)

## 🎮 Usage

### 📊 Paper Trading (Safe Default)
```bash
# Basic autonomous trading (paper mode)
python -m crypto_trader.autonomous_main

# Custom parameters
python -m crypto_trader.autonomous_main \
  --max-positions 3 \
  --max-allocation 0.25 \
  --target-volatility 0.15
```

### 💰 Live Trading (Real Money)
```bash
# Live trading (requires confirmation)
python -m crypto_trader.autonomous_main \
  --live-trading \
  --confirm

# You'll need to type "CONFIRM LIVE TRADING" to proceed
```

### 🔧 Configuration Options
```bash
--paper-trading          # Paper trading mode (default)
--live-trading          # Live trading mode (requires --confirm)
--confirm              # Confirm live trading
--max-positions N      # Max concurrent positions (1-10, default: 5)
--max-allocation F     # Max allocation per asset (0.05-0.5, default: 0.3)
--target-volatility F  # Target portfolio volatility (0.1-0.5, default: 0.2)
--output DIR          # Output directory (default: output)
--verbose             # Enable verbose logging
--show-models         # Show model assignments
```

### 📋 View Model Assignments
```bash
python -m crypto_trader.autonomous_main --show-models
```

## 🛡️ Safety Features

### 🔐 Built-in Risk Controls
- **Paper Trading Default**: Always starts in safe simulation mode
- **Position Limits**: Maximum 10 concurrent positions
- **Allocation Caps**: Maximum 50% per single asset
- **Volatility Controls**: Target portfolio volatility limits
- **Stop Losses**: Automatic stop-loss placement
- **Daily Loss Limits**: Maximum daily loss protection

### 🚨 Live Trading Safeguards
- **Double Confirmation**: Requires `--confirm` flag + manual confirmation
- **API Permission Check**: Validates Binance API permissions
- **Position Size Validation**: Validates all orders before execution
- **Real-time Monitoring**: Continuous risk monitoring
- **Emergency Controls**: Ability to halt trading immediately

## 📈 System Architecture

### 🔄 Autonomous Trading Flow
1. **Market Scanning** → Discover opportunities across 50+ cryptocurrencies
2. **Asset Selection** → AI selects 3-5 optimal assets for trading
3. **Data Collection** → Gather comprehensive market data and news
4. **Analysis** → Multi-dimensional analysis (technical + fundamental + sentiment)
5. **Risk Assessment** → Calculate optimal position sizes and risk controls
6. **Portfolio Optimization** → Optimize allocation across selected assets
7. **Trade Execution** → Execute trades with optimal timing and order types
8. **Performance Monitoring** → Track performance and optimize strategy
9. **Strategy Coordination** → Master oversight and decision making

### 🏗️ Multi-Agent Coordination
The system uses sequential task execution with context passing:
```
Market Scanner → Asset Selector → Market Data Analyst
                                         ↓
News Researcher → Crypto Analyst → Risk Manager
                                         ↓
Portfolio Manager → Trade Executor → Performance Monitor
                                         ↓
                    Strategy Coordinator (Master)
```

## 📊 Output and Monitoring

### 📁 Generated Files
- **Strategy Reports**: Detailed analysis and trading plans
- **Performance Metrics**: Real-time performance tracking
- **Risk Assessments**: Portfolio risk analysis
- **Trade Logs**: Complete audit trail of all trades

### 📋 Example Output Structure
```
output/
├── autonomous_trading_strategy_20250108_143022.md
├── performance_metrics_20250108.json
├── risk_assessment_20250108.json
└── trade_log_20250108.csv
```

## ⚠️ Important Disclaimers

### 🚨 Trading Risks
- **Cryptocurrency trading involves substantial risk of loss**
- **Past performance does not guarantee future results**  
- **Only trade with capital you can afford to lose**
- **This system is experimental and not financial advice**

### 🔧 System Limitations
- Requires stable internet connection
- Depends on external API availability
- AI decisions can be unpredictable
- Market conditions can change rapidly

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/edofransisco011/CryptoTrader_Agents/issues)
- **Documentation**: Check the `docs/` directory
- **Discord**: Join our trading community

---

### ⚡ Quick Start Commands

```bash
# 1. Setup
git clone https://github.com/edofransisco011/CryptoTrader_Agents.git
cd CryptoTrader_Agents
cp .env.example .env
# Edit .env with your IONOS API key

# 2. Install
pip install -e .

# 3. Test (Paper Trading)
python -m crypto_trader.autonomous_main --show-models
python -m crypto_trader.autonomous_main

# 4. Monitor Results
ls output/
```

**🎯 Ready to revolutionize your crypto trading with AI? Start with paper trading and see the autonomous system in action!** 🚀