"""
Portfolio Simulator Tool for CrewAI Agents
Provides interface for virtual trading and portfolio management
"""
import json
import logging
from typing import Dict, Any, Optional
from crewai.tools import BaseTool
from pydantic import Field

from ..portfolio_simulator import PortfolioSimulator

logger = logging.getLogger("crypto_trader.tools.portfolio_simulator_tool")

class PortfolioSimulatorTool(BaseTool):
    """
    Tool for virtual portfolio management and trade simulation.
    
    This tool provides agents with the ability to execute virtual trades,
    check portfolio status, and manage positions in test mode.
    """
    
    name: str = "Portfolio Simulator Tool"
    description: str = (
        "Virtual portfolio management and trade simulation tool. "
        "Actions: 'get_portfolio_status', 'execute_buy_order', 'execute_sell_order', "
        "'get_position_info', 'get_available_balance', 'calculate_position_size'"
    )
    
    portfolio_simulator: PortfolioSimulator = Field(description="Portfolio simulator instance")
    
    def _run(self, action: str, parameters: Dict[str, Any]) -> str:
        """Execute portfolio simulation actions"""
        try:
            if action == "get_portfolio_status":
                return self._get_portfolio_status(parameters)
            elif action == "execute_buy_order":
                return self._execute_buy_order(parameters)
            elif action == "execute_sell_order":
                return self._execute_sell_order(parameters)
            elif action == "get_position_info":
                return self._get_position_info(parameters)
            elif action == "get_available_balance":
                return self._get_available_balance(parameters)
            elif action == "calculate_position_size":
                return self._calculate_position_size(parameters)
            else:
                return json.dumps({
                    "error": f"Unknown action: {action}",
                    "available_actions": [
                        "get_portfolio_status", "execute_buy_order", "execute_sell_order",
                        "get_position_info", "get_available_balance", "calculate_position_size"
                    ]
                })
        except Exception as e:
            logger.error(f"Portfolio simulator tool error: {e}")
            return json.dumps({"error": str(e)})
    
    def _get_portfolio_status(self, parameters: Dict[str, Any]) -> str:
        """Get current portfolio status including positions and performance"""
        try:
            current_prices = parameters.get('current_prices', {})
            
            # Get portfolio summary
            summary = self.portfolio_simulator.get_portfolio_summary(current_prices)
            
            # Add additional status information
            status = {
                "portfolio_summary": summary,
                "recent_trades": [
                    trade.to_dict() for trade in self.portfolio_simulator.trades[-5:]
                ],
                "position_details": {
                    symbol: pos.to_dict() 
                    for symbol, pos in self.portfolio_simulator.positions.items()
                },
                "simulation_stats": {
                    "days_running": summary["days_running"],
                    "total_trades": summary["total_trades"],
                    "success_rate": self._calculate_success_rate(),
                    "average_trade_size": self._calculate_average_trade_size(),
                    "largest_position": self._get_largest_position()
                }
            }
            
            return json.dumps(status, default=str)
            
        except Exception as e:
            return json.dumps({"error": f"Failed to get portfolio status: {str(e)}"})
    
    def _execute_buy_order(self, parameters: Dict[str, Any]) -> str:
        """Execute a buy order with specified parameters"""
        try:
            symbol = parameters.get('symbol')
            usd_amount = float(parameters.get('usd_amount', 0))
            current_price = float(parameters.get('current_price', 0))
            reasoning = parameters.get('reasoning', '')
            
            if not symbol or usd_amount <= 0 or current_price <= 0:
                return json.dumps({
                    "error": "Invalid parameters",
                    "required": "symbol, usd_amount > 0, current_price > 0",
                    "provided": parameters
                })
            
            # Execute the buy order
            trade = self.portfolio_simulator.execute_buy_order(
                symbol=symbol,
                usd_amount=usd_amount,
                current_price=current_price,
                reasoning=reasoning
            )
            
            if trade:
                return json.dumps({
                    "success": True,
                    "trade": trade.to_dict(),
                    "new_position": self.portfolio_simulator.get_position_info(symbol).to_dict() if self.portfolio_simulator.get_position_info(symbol) else None,
                    "remaining_balance": self.portfolio_simulator.get_available_balance()
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Buy order execution failed",
                    "available_balance": self.portfolio_simulator.get_available_balance()
                })
                
        except Exception as e:
            return json.dumps({"error": f"Failed to execute buy order: {str(e)}"})
    
    def _execute_sell_order(self, parameters: Dict[str, Any]) -> str:
        """Execute a sell order with specified parameters"""
        try:
            symbol = parameters.get('symbol')
            quantity = float(parameters.get('quantity', 0))
            current_price = float(parameters.get('current_price', 0))
            reasoning = parameters.get('reasoning', '')
            
            if not symbol or quantity <= 0 or current_price <= 0:
                return json.dumps({
                    "error": "Invalid parameters",
                    "required": "symbol, quantity > 0, current_price > 0",
                    "provided": parameters
                })
            
            # Execute the sell order
            trade = self.portfolio_simulator.execute_sell_order(
                symbol=symbol,
                quantity=quantity,
                current_price=current_price,
                reasoning=reasoning
            )
            
            if trade:
                return json.dumps({
                    "success": True,
                    "trade": trade.to_dict(),
                    "remaining_position": self.portfolio_simulator.get_position_info(symbol).to_dict() if self.portfolio_simulator.get_position_info(symbol) else None,
                    "new_balance": self.portfolio_simulator.get_available_balance()
                })
            else:
                return json.dumps({
                    "success": False,
                    "error": "Sell order execution failed",
                    "current_position": self.portfolio_simulator.get_position_info(symbol).to_dict() if self.portfolio_simulator.get_position_info(symbol) else None
                })
                
        except Exception as e:
            return json.dumps({"error": f"Failed to execute sell order: {str(e)}"})
    
    def _get_position_info(self, parameters: Dict[str, Any]) -> str:
        """Get information about a specific position"""
        try:
            symbol = parameters.get('symbol')
            if not symbol:
                return json.dumps({"error": "Symbol parameter required"})
            
            position = self.portfolio_simulator.get_position_info(symbol)
            if position:
                return json.dumps({
                    "has_position": True,
                    "position": position.to_dict()
                })
            else:
                return json.dumps({
                    "has_position": False,
                    "symbol": symbol
                })
                
        except Exception as e:
            return json.dumps({"error": f"Failed to get position info: {str(e)}"})
    
    def _get_available_balance(self, parameters: Dict[str, Any]) -> str:
        """Get available USD balance for trading"""
        try:
            balance = self.portfolio_simulator.get_available_balance()
            return json.dumps({
                "available_balance": balance,
                "formatted": f"${balance:,.2f}"
            })
        except Exception as e:
            return json.dumps({"error": f"Failed to get balance: {str(e)}"})
    
    def _calculate_position_size(self, parameters: Dict[str, Any]) -> str:
        """Calculate appropriate position size based on risk parameters"""
        try:
            symbol = parameters.get('symbol')
            current_price = float(parameters.get('current_price', 0))
            risk_percentage = float(parameters.get('risk_percentage', 0.05))  # Default 5%
            max_position_percentage = float(parameters.get('max_position_percentage', 0.30))  # Default 30%
            
            if not symbol or current_price <= 0:
                return json.dumps({"error": "Symbol and current_price required"})
            
            available_balance = self.portfolio_simulator.get_available_balance()
            current_positions_value = sum(
                pos.current_value for pos in self.portfolio_simulator.positions.values()
            )
            total_portfolio_value = available_balance + current_positions_value
            
            # Calculate position size based on risk parameters
            risk_based_size = total_portfolio_value * risk_percentage
            max_position_size = total_portfolio_value * max_position_percentage
            balance_based_size = available_balance * 0.95  # Leave 5% cash buffer
            
            # Take the minimum to ensure constraints are met
            suggested_usd_amount = min(risk_based_size, max_position_size, balance_based_size)
            suggested_quantity = suggested_usd_amount / current_price if current_price > 0 else 0
            
            return json.dumps({
                "symbol": symbol,
                "current_price": current_price,
                "suggested_usd_amount": suggested_usd_amount,
                "suggested_quantity": suggested_quantity,
                "risk_percentage": risk_percentage,
                "max_position_percentage": max_position_percentage,
                "calculations": {
                    "available_balance": available_balance,
                    "total_portfolio_value": total_portfolio_value,
                    "risk_based_size": risk_based_size,
                    "max_position_size": max_position_size,
                    "balance_based_size": balance_based_size
                }
            })
            
        except Exception as e:
            return json.dumps({"error": f"Failed to calculate position size: {str(e)}"})
    
    def _calculate_success_rate(self) -> float:
        """Calculate trading success rate"""
        if not self.portfolio_simulator.trades:
            return 0.0
        
        profitable_trades = 0
        total_trades = 0
        
        # Group trades by symbol to calculate P&L
        symbol_trades = {}
        for trade in self.portfolio_simulator.trades:
            if trade.symbol not in symbol_trades:
                symbol_trades[trade.symbol] = []
            symbol_trades[trade.symbol].append(trade)
        
        # Calculate P&L for each completed trade pair (buy -> sell)
        for symbol, trades in symbol_trades.items():
            buys = [t for t in trades if t.side == 'BUY']
            sells = [t for t in trades if t.side == 'SELL']
            
            for sell in sells:
                # Find corresponding buy (simplified - takes first available)
                if buys:
                    buy = buys.pop(0)
                    pnl = (sell.price - buy.price) * sell.quantity - sell.fee - buy.fee
                    if pnl > 0:
                        profitable_trades += 1
                    total_trades += 1
        
        return (profitable_trades / total_trades * 100) if total_trades > 0 else 0.0
    
    def _calculate_average_trade_size(self) -> float:
        """Calculate average trade size in USD"""
        if not self.portfolio_simulator.trades:
            return 0.0
        
        total_value = sum(trade.value for trade in self.portfolio_simulator.trades)
        return total_value / len(self.portfolio_simulator.trades)
    
    def _get_largest_position(self) -> Optional[str]:
        """Get the symbol of the largest position by value"""
        if not self.portfolio_simulator.positions:
            return None
        
        largest_pos = max(
            self.portfolio_simulator.positions.values(),
            key=lambda pos: pos.current_value
        )
        return largest_pos.symbol