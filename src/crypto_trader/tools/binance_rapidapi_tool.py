# src/crypto_trader/tools/binance_rapidapi_tool.py
import os
import requests
import json
from typing import Type, Optional, Literal, Dict, Any
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

# --- Input Schemas for different Binance RapidAPI actions ---

class KlineDataInput(BaseModel):
    """Input for fetching Kline/Candlestick data."""
    symbol: str = Field(..., description="Trading symbol (e.g., 'BTCUSDT', 'ETHBTC').")
    interval: str = Field(..., description="Kline interval (e.g., '1m', '1h', '1d').")
    startTime: Optional[int] = Field(None, description="Start time in milliseconds (Unix timestamp). Optional.")
    endTime: Optional[int] = Field(None, description="End time in milliseconds (Unix timestamp). Optional.")
    limit: Optional[int] = Field(None, description="Number of klines to retrieve. Default 500, max depends on API. Optional.")

class SymbolPriceTickerInput(BaseModel):
    """Input for fetching symbol price ticker."""
    symbol: Optional[str] = Field(None, description="Trading symbol (e.g., 'BTCUSDT'). If omitted, prices for all symbols might be returned.")

class Ticker24hrInput(BaseModel):
    """Input for fetching 24hr ticker price change statistics."""
    symbol: Optional[str] = Field(None, description="Trading symbol (e.g., 'BTCUSDT'). If omitted, stats for all symbols might be returned.")


class BinanceRapidApiToolInput(BaseModel):
    """
    Defines the action and corresponding parameters for the Binance RapidAPI tool.
    """
    action: Literal['get_kline_data', 'get_symbol_price_ticker', 'get_24hr_ticker'] = Field(..., description="The Binance API action to perform.")
    parameters: Dict[str, Any] = Field(..., description="A dictionary of parameters specific to the chosen action.")

class BinanceRapidApiTool(BaseTool):
    name: str = "Binance Market Data Tool (via RapidAPI)"
    description: str = (
        "A tool to interact with Binance market data endpoints via RapidAPI. "
        "Supports actions: 'get_kline_data' for historical OHLCV, "
        "'get_symbol_price_ticker' for current prices, and "
        "'get_24hr_ticker' for 24-hour price change statistics. "
        "Input to this tool should be a JSON object with 'action' and 'parameters' keys."
    )
    args_schema: Type[BaseModel] = BinanceRapidApiToolInput
    rapidapi_key: Optional[str] = None
    rapidapi_host: Optional[str] = None
    
    # Updated endpoint paths based on your http.client examples
    kline_endpoint_path: str = "/klines" 
    price_ticker_endpoint_path: str = "/ticker/price"
    ticker_24hr_endpoint_path: str = "/ticker/24hr"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
        self.rapidapi_host = os.getenv("RAPIDAPI_BINANCE_HOST")
        
        if not self.rapidapi_key or not self.rapidapi_host:
            try:
                from dotenv import load_dotenv
                load_dotenv()
                self.rapidapi_key = os.getenv("RAPIDAPI_KEY")
                self.rapidapi_host = os.getenv("RAPIDAPI_BINANCE_HOST")
            except ImportError:
                print("python-dotenv not installed. API key and host must be available in environment.")

        if not self.rapidapi_key:
            raise ValueError("RAPIDAPI_KEY environment variable not set. Please set it.")
        if not self.rapidapi_host:
            raise ValueError("RAPIDAPI_BINANCE_HOST environment variable not set. Please set it to 'binance43.p.rapidapi.com' or your specific host.")

    def _make_request(self, endpoint_path: str, params: Optional[Dict[str, Any]] = None) -> str:
        # Ensure params are suitable for query string (requests library handles this conversion)
        query_params = {k: v for k, v in params.items() if v is not None} if params else None
        
        url = f"https://{self.rapidapi_host}{endpoint_path}"
        headers = {
            "x-rapidapi-key": self.rapidapi_key, # Corrected to lowercase 'x' as per http.client example
            "x-rapidapi-host": self.rapidapi_host # Corrected to lowercase 'x'
        }
        try:
            response = requests.get(url, headers=headers, params=query_params)
            response.raise_for_status()
            return json.dumps(response.json())
        except requests.exceptions.HTTPError as e:
            return f"HTTP Error: {e.response.status_code} - {e.response.text} for URL: {url} with params: {query_params}"
        except Exception as e:
            return f"Error making request to {url}: {str(e)}"

    def _run(self, action: Literal['get_kline_data', 'get_symbol_price_ticker', 'get_24hr_ticker'], parameters: Dict[str, Any]) -> str:
        if action == "get_kline_data":
            try:
                # Ensure all required parameters are present or handled if optional
                # For klines, 'symbol' and 'interval' are typically mandatory by Binance direct API
                # RapidAPI might have different behavior, but tool should pass what's given.
                validated_params = KlineDataInput(**parameters) 
                return self._make_request(self.kline_endpoint_path, validated_params.model_dump(exclude_none=True))
            except Exception as e: 
                return f"Error processing 'get_kline_data': Invalid parameters or other issue. {str(e)}. Parameters: {parameters}"
        
        elif action == "get_symbol_price_ticker":
            try:
                validated_params = SymbolPriceTickerInput(**parameters)
                return self._make_request(self.price_ticker_endpoint_path, validated_params.model_dump(exclude_none=True))
            except Exception as e:
                return f"Error processing 'get_symbol_price_ticker': {str(e)}. Parameters: {parameters}"

        elif action == "get_24hr_ticker":
            try:
                validated_params = Ticker24hrInput(**parameters)
                return self._make_request(self.ticker_24hr_endpoint_path, validated_params.model_dump(exclude_none=True))
            except Exception as e:
                return f"Error processing 'get_24hr_ticker': {str(e)}. Parameters: {parameters}"
        else:
            return f"Error: Invalid action '{action}' specified."

# --- Example Usage (for testing the tool directly) ---
if __name__ == "__main__":
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    dotenv_path = os.path.join(project_root, ".env")
    try:
        from dotenv import load_dotenv
        if os.path.exists(dotenv_path):
            load_dotenv(dotenv_path)
            print(f".env loaded from: {dotenv_path}")
        else:
            print(f".env file not found at: {dotenv_path}. Ensure it's in the project root.")
    except ImportError:
        print("python-dotenv not installed. API keys must be in environment for direct tool testing.")

    if not os.getenv("RAPIDAPI_KEY") or not os.getenv("RAPIDAPI_BINANCE_HOST"):
        print("Please set RAPIDAPI_KEY and RAPIDAPI_BINANCE_HOST in your .env file (in project root) to test this tool.")
    else:
        binance_tool = BinanceRapidApiTool()
        print(f"BinanceRapidApiTool initialized for direct testing with host: {binance_tool.rapidapi_host}")

        print("\n--- Testing Get Kline Data ---")
        # Parameters match your http.client example for klines
        kline_params = {"symbol": "ETHBTC", "interval": "1m", "limit": 3} # Reduced limit for faster test
        kline_result = binance_tool._run(action="get_kline_data", parameters=kline_params)
        print(f"Kline Data for ETHBTC (1m, limit 3):\n{kline_result}\n")

        print("\n--- Testing Get Symbol Price Ticker (All Symbols as per your example) ---")
        # Your example showed no parameters, implying all symbols.
        # The SymbolPriceTickerInput makes 'symbol' optional.
        price_params_all = {} 
        price_result_all = binance_tool._run(action="get_symbol_price_ticker", parameters=price_params_all)
        # Printing only a part of it as it can be very long
        print(f"Price Ticker for All Symbols (first 300 chars):\n{price_result_all[:300]}...\n")
        
        print("\n--- Testing Get Symbol Price Ticker (Single Symbol) ---")
        price_params_single = {"symbol": "BTCUSDT"} 
        price_result_single = binance_tool._run(action="get_symbol_price_ticker", parameters=price_params_single)
        print(f"Price Ticker for BTCUSDT:\n{price_result_single}\n")


        print("\n--- Testing Get 24hr Ticker (All Symbols as per your example) ---")
        # Your example showed no parameters, implying all symbols.
        # The Ticker24hrInput makes 'symbol' optional.
        ticker_24hr_params_all = {}
        ticker_24hr_result_all = binance_tool._run(action="get_24hr_ticker", parameters=ticker_24hr_params_all)
        print(f"24hr Ticker for All Symbols (first 300 chars):\n{ticker_24hr_result_all[:300]}...\n")

        print("\n--- Testing Get 24hr Ticker (Single Symbol) ---")
        ticker_24hr_params_single = {"symbol": "ETHUSDT"}
        ticker_24hr_result_single = binance_tool._run(action="get_24hr_ticker", parameters=ticker_24hr_params_single)
        print(f"24hr Ticker for ETHUSDT:\n{ticker_24hr_result_single}\n")