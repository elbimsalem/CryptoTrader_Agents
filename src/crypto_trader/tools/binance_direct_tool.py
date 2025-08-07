"""
Direct Binance API Tool for autonomous trading
"""
import os
import time
import hmac
import hashlib
import requests
import json
from typing import Dict, Any, List, Optional, Literal
from decimal import Decimal
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
from dotenv import load_dotenv

class BinanceDirectTool(BaseTool):
    """
    Direct Binance API tool for market data and trading operations
    """
    name: str = "Binance Direct API Tool"
    description: str = (
        "A comprehensive tool for interacting directly with Binance API. "
        "Supports market data retrieval, account information, and trade execution. "
        "Actions: 'get_exchange_info', 'get_ticker_24hr', 'get_klines', 'get_orderbook', "
        "'get_account_info', 'get_open_orders', 'place_order', 'cancel_order', 'get_top_symbols'"
    )
    
    # Define fields as model fields for Pydantic compatibility
    api_key: Optional[str] = Field(default=None)
    api_secret: Optional[str] = Field(default=None)
    base_url: str = Field(default="https://api.binance.com")
    
    def __init__(self, **kwargs):
        # Initialize with API credentials from environment
        load_dotenv()
        
        # Set default values from environment
        if 'api_key' not in kwargs:
            kwargs['api_key'] = os.getenv("BINANCE_API_KEY")
        if 'api_secret' not in kwargs:
            kwargs['api_secret'] = os.getenv("BINANCE_API_SECRET")
        
        super().__init__(**kwargs)
        
        if not self.api_key or not self.api_secret:
            print("Warning: Binance API credentials not found. Only public endpoints will work.")
    
    def _generate_signature(self, params: str) -> str:
        """Generate HMAC SHA256 signature for authenticated requests"""
        return hmac.new(
            self.api_secret.encode('utf-8'), 
            params.encode('utf-8'), 
            hashlib.sha256
        ).hexdigest()
    
    def _make_request(self, endpoint: str, method: str = "GET", params: Dict = None, signed: bool = False) -> Dict:
        """Make request to Binance API"""
        if params is None:
            params = {}
        
        url = f"{self.base_url}{endpoint}"
        headers = {"X-MBX-APIKEY": self.api_key} if self.api_key else {}
        
        if signed:
            params['timestamp'] = int(time.time() * 1000)
            query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
            params['signature'] = self._generate_signature(query_string)
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers, params=params)
            elif method == "POST":
                response = requests.post(url, headers=headers, params=params)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers, params=params)
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": f"Request failed: {str(e)}"}
    
    def _run(self, action: str, parameters: Dict[str, Any] = None) -> str:
        """Execute the specified action with parameters"""
        if parameters is None:
            parameters = {}
            
        try:
            if action == "get_exchange_info":
                result = self._get_exchange_info()
            elif action == "get_ticker_24hr":
                result = self._get_ticker_24hr(parameters.get("symbol"))
            elif action == "get_klines":
                result = self._get_klines(parameters)
            elif action == "get_orderbook":
                result = self._get_orderbook(parameters)
            elif action == "get_account_info":
                result = self._get_account_info()
            elif action == "get_open_orders":
                result = self._get_open_orders(parameters.get("symbol"))
            elif action == "place_order":
                result = self._place_order(parameters)
            elif action == "cancel_order":
                result = self._cancel_order(parameters)
            elif action == "get_top_symbols":
                result = self._get_top_symbols(parameters.get("limit", 20))
            else:
                result = {"error": f"Unknown action: {action}"}
            
            return json.dumps(result, default=str, indent=2)
        except Exception as e:
            return json.dumps({"error": f"Error executing {action}: {str(e)}"})
    
    def _get_exchange_info(self) -> Dict:
        """Get exchange trading rules and symbol information"""
        return self._make_request("/api/v3/exchangeInfo")
    
    def _get_ticker_24hr(self, symbol: Optional[str] = None) -> Dict:
        """Get 24hr ticker statistics"""
        params = {"symbol": symbol} if symbol else {}
        return self._make_request("/api/v3/ticker/24hr", params=params)
    
    def _get_klines(self, parameters: Dict) -> Dict:
        """Get kline/candlestick data"""
        required_params = ["symbol", "interval"]
        for param in required_params:
            if param not in parameters:
                return {"error": f"Missing required parameter: {param}"}
        
        params = {
            "symbol": parameters["symbol"],
            "interval": parameters["interval"],
            "limit": parameters.get("limit", 500)
        }
        
        if "startTime" in parameters:
            params["startTime"] = parameters["startTime"]
        if "endTime" in parameters:
            params["endTime"] = parameters["endTime"]
        
        return self._make_request("/api/v3/klines", params=params)
    
    def _get_orderbook(self, parameters: Dict) -> Dict:
        """Get order book depth"""
        if "symbol" not in parameters:
            return {"error": "Missing required parameter: symbol"}
        
        params = {
            "symbol": parameters["symbol"],
            "limit": parameters.get("limit", 100)
        }
        
        return self._make_request("/api/v3/depth", params=params)
    
    def _get_account_info(self) -> Dict:
        """Get account information"""
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials required for account information"}
        
        return self._make_request("/api/v3/account", signed=True)
    
    def _get_open_orders(self, symbol: Optional[str] = None) -> Dict:
        """Get open orders"""
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials required for order information"}
        
        params = {"symbol": symbol} if symbol else {}
        return self._make_request("/api/v3/openOrders", params=params, signed=True)
    
    def _place_order(self, parameters: Dict) -> Dict:
        """Place a new order"""
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials required for placing orders"}
        
        required_params = ["symbol", "side", "type", "quantity"]
        for param in required_params:
            if param not in parameters:
                return {"error": f"Missing required parameter: {param}"}
        
        # Build order parameters
        params = {
            "symbol": parameters["symbol"],
            "side": parameters["side"],  # BUY or SELL
            "type": parameters["type"],  # MARKET, LIMIT, etc.
            "quantity": parameters["quantity"]
        }
        
        # Add optional parameters based on order type
        if parameters["type"] in ["LIMIT", "STOP_LOSS_LIMIT", "TAKE_PROFIT_LIMIT"]:
            if "price" not in parameters:
                return {"error": "Price required for limit orders"}
            params["price"] = parameters["price"]
            params["timeInForce"] = parameters.get("timeInForce", "GTC")
        
        if "stopPrice" in parameters:
            params["stopPrice"] = parameters["stopPrice"]
        
        return self._make_request("/api/v3/order", method="POST", params=params, signed=True)
    
    def _cancel_order(self, parameters: Dict) -> Dict:
        """Cancel an order"""
        if not self.api_key or not self.api_secret:
            return {"error": "API credentials required for canceling orders"}
        
        if "symbol" not in parameters:
            return {"error": "Missing required parameter: symbol"}
        
        if "orderId" not in parameters and "origClientOrderId" not in parameters:
            return {"error": "Either orderId or origClientOrderId is required"}
        
        params = {"symbol": parameters["symbol"]}
        if "orderId" in parameters:
            params["orderId"] = parameters["orderId"]
        if "origClientOrderId" in parameters:
            params["origClientOrderId"] = parameters["origClientOrderId"]
        
        return self._make_request("/api/v3/order", method="DELETE", params=params, signed=True)
    
    def _get_top_symbols(self, limit: int = 20) -> Dict:
        """Get top trading symbols by volume"""
        try:
            tickers = self._make_request("/api/v3/ticker/24hr")
            
            if isinstance(tickers, list):
                # Filter USDT pairs and sort by volume
                usdt_pairs = [
                    ticker for ticker in tickers 
                    if ticker["symbol"].endswith("USDT") and 
                    float(ticker["quoteVolume"]) > 1000000  # Min $1M volume
                ]
                
                # Sort by quote volume (trading volume in USDT)
                top_symbols = sorted(
                    usdt_pairs, 
                    key=lambda x: float(x["quoteVolume"]), 
                    reverse=True
                )[:limit]
                
                return {
                    "top_symbols": [
                        {
                            "symbol": symbol["symbol"],
                            "price": float(symbol["lastPrice"]),
                            "change_24h": float(symbol["priceChangePercent"]),
                            "volume_24h": float(symbol["quoteVolume"]),
                            "trades_24h": int(symbol["count"])
                        }
                        for symbol in top_symbols
                    ]
                }
            else:
                return {"error": "Failed to fetch ticker data"}
                
        except Exception as e:
            return {"error": f"Error fetching top symbols: {str(e)}"}


# Input schema for the tool
class BinanceDirectToolInput(BaseModel):
    action: str = Field(..., description="The action to perform")
    parameters: Optional[Dict[str, Any]] = Field(default={}, description="Parameters for the action")