# CryptoTrader Documentation

## Overview

CryptoTrader is an AI-driven cryptocurrency trading plan generator powered by [crewAI](https://crewai.com). The system employs multiple AI agents that collaborate to analyze cryptocurrency market data, research news and sentiment, and develop actionable trading strategies.

## Project Structure

```
crypto_trader/
├── output/            # Directory for storing generated trading plans
├── .venv/             # Python virtual environment
├── knowledge/         # Knowledge base for the project
├── src/               # Source code
│   └── crypto_trader/
│       ├── config/
│       │   ├── agents.yaml  # Agent configurations
│       │   └── tasks.yaml   # Task configurations
│       ├── tools/
│       │   └── binance_rapidapi_tool.py  # Tool for Binance API interactions
│       ├── crew.py    # Main crew definition with agents and tasks
│       ├── main.py    # Entry point and CLI interface
│       └── __init__.py
├── tests/             # Unit tests directory
├── README.md          # Project documentation
├── pyproject.toml     # Project configuration
└── .gitignore         # Git ignore file
```

## Installation and Setup

### Prerequisites
- Python 3.10 or higher (< 3.13)
- UV for dependency management

### Installation Steps
1. Install UV:
```bash
pip install uv
```

2. Clone the repository and navigate to the project directory

3. Install dependencies:
```bash
crewai install
```

4. Configure API keys:
   - Add `OPENAI_API_KEY` to `.env` file (for LLM access)
   - Add `RAPIDAPI_KEY` and `RAPIDAPI_BINANCE_HOST` to `.env` file (for Binance data access)
   - Add `SERPER_API_KEY` to `.env` file (for web search capabilities)

## Core Components

### AI Agents & IONOS Cloud LLM Configuration

The system employs multiple specialized AI agents powered by IONOS Cloud models:

#### Agent LLM Model Assignments:

| Agent | Model | Temperature | Max Tokens | Purpose |
|-------|-------|-------------|------------|---------|
| **Market Scanner** | `mistralai/Mixtral-8x7B-Instruct-v0.1` | 0.0 | 2000 | Fast, efficient market scanning |
| **Asset Selector** | `meta-llama/Llama-3.3-70B-Instruct` | 0.1 | 3000 | Balanced asset selection analysis |
| **Market Data Analyst** | `mistralai/Mistral-Nemo-Instruct-2407` | 0.0 | 3000 | Efficient data analysis |
| **News Researcher** | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | 0.1 | 4000 | Large model for sentiment analysis |
| **Crypto Analyst** | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | 0.1 | 6000 | Comprehensive analysis (largest tokens) |
| **Risk Manager** | `meta-llama/Llama-3.3-70B-Instruct` | 0.0 | 3000 | Conservative risk calculations |
| **Portfolio Manager** | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | 0.05 | 4000 | Very conservative portfolio optimization |
| **Trade Executor** | `meta-llama/CodeLlama-13b-Instruct-hf` | 0.0 | 2000 | Code-specialized for execution logic |
| **Performance Monitor** | `mistralai/Mistral-Small-24B-Instruct` | 0.0 | 3000 | Efficient monitoring and reporting |
| **Strategy Coordinator** | `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` | 0.1 | 5000 | Strategic coordination |

#### Model Configuration Details:

**Mistral Models:**
```python
# Market Scanner Agent
model="openai/mistralai/Mixtral-8x7B-Instruct-v0.1"
temperature=0.0  # Deterministic for data processing
max_tokens=2000
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"

# Market Data Analyst Agent  
model="openai/mistralai/Mistral-Nemo-Instruct-2407"
temperature=0.0  # Deterministic for data analysis
max_tokens=3000
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"

# Performance Monitor Agent
model="openai/mistralai/Mistral-Small-24B-Instruct"
temperature=0.0  # Factual reporting
max_tokens=3000
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"
```

**Llama Models:**
```python
# Asset Selector & Risk Manager
model="openai/meta-llama/Llama-3.3-70B-Instruct"
temperature=0.0-0.1  # Conservative to slight creativity
max_tokens=3000
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"

# News Researcher, Crypto Analyst, Portfolio Manager, Strategy Coordinator
model="openai/meta-llama/Meta-Llama-3.1-405B-Instruct-FP8"
temperature=0.05-0.1  # Very conservative to balanced
max_tokens=4000-6000  # Varies by agent needs
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"

# Trade Executor
model="openai/meta-llama/CodeLlama-13b-Instruct-hf"
temperature=0.0  # Deterministic for trade execution
max_tokens=2000
timeout=120
openai_api_base="https://openai.inference.de-txl.ionos.com/v1"
```

#### Model Usage Summary:
- **Most Used**: `meta-llama/Meta-Llama-3.1-405B-Instruct-FP8` (4 agents - highest reasoning)
- **Balanced**: `meta-llama/Llama-3.3-70B-Instruct` (2 agents - medium cost)
- **Efficient**: Various Mistral models (3 agents - fast/low cost)
- **Specialized**: `meta-llama/CodeLlama-13b-Instruct-hf` (1 agent - code execution)

### Tasks

The agents collaborate on a sequence of tasks:

1. **Fetch Binance Klines Task**: Retrieve historical candlestick data
2. **Fetch Binance Price Ticker Task**: Get current price information
3. **Fetch Binance 24hr Stats Task**: Get 24-hour market statistics
4. **Research News and Sentiment Task**: Gather and analyze recent news
5. **Analyze Crypto Data Task**: Synthesize market data and news
6. **Develop Trading Plan Task**: Create an actionable trading strategy

### Tools

The project uses custom and third-party tools:

1. **BinanceRapidApiTool**: Custom tool for accessing Binance cryptocurrency data via RapidAPI
2. **SerperDevTool**: For web searching capabilities (from crewai_tools)
3. **ScrapeWebsiteTool**: For extracting information from web pages (from crewai_tools)

## Usage

### Basic Usage

Run the project with default configuration:

```bash
crewai run
```

This will:
1. Generate a trading plan for the default cryptocurrency (PEPEUSDT)
2. Save the report to the `output/` directory

### Advanced Usage

Customize the execution with command-line arguments:

```bash
python -m src.crypto_trader.main --symbol BTCUSDT --interval 1h --limit 100 --output custom_output --verbose
```

Available parameters:
- `--symbol` or `-s`: Cryptocurrency trading symbol (default: PEPEUSDT)
- `--interval` or `-i`: Kline interval (default: 4h)
- `--limit` or `-l`: Number of klines to fetch (default: 72)
- `--output` or `-o`: Output directory (default: output)
- `--verbose` or `-v`: Enable verbose logging

## Output

The system generates a comprehensive trading plan in Markdown format containing:

1. Market data analysis (price, volume, trends)
2. News and sentiment analysis
3. Support and resistance levels
4. Entry and exit points
5. Risk management strategies
6. Profit targets

The output is saved to a file named `trading_plan_{target_symbol}_{datetime}.md` in the output directory.

## Extending the Project

### Adding New Agents

1. Define the agent in `src/crypto_trader/config/agents.yaml`
2. Implement the agent class in `src/crypto_trader/crew.py`
3. Add associated tasks in `src/crypto_trader/config/tasks.yaml`

### Adding New Tools

1. Create a new tool in `src/crypto_trader/tools/`
2. Implement the tool following the crewAI BaseTool pattern
3. Add the tool to the appropriate agent in `src/crypto_trader/crew.py`

## Troubleshooting

Common issues:

1. **API Key Errors**: Ensure all required API keys are properly set in the `.env` file
2. **Dependency Issues**: Make sure UV is installed and dependencies are properly locked
3. **Rate Limiting**: If hitting RapidAPI rate limits, consider implementing retry logic or upgrading your plan

## Dependencies

- crewai: Framework for multi-agent AI systems
- requests: For API interactions
- pydantic: For data validation
- python-dotenv: For environment variable management

## License

See LICENSE file for details. 
