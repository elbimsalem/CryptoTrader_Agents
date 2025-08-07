"""
Portfolio Simulator for Test Mode
Handles virtual trading, balance tracking, and performance calculation
"""
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import os

logger = logging.getLogger("crypto_trader.portfolio_simulator")

@dataclass
class Trade:
    """Represents a single trade execution"""
    trade_id: str
    timestamp: datetime
    symbol: str
    side: str  # 'BUY' or 'SELL'
    quantity: float
    price: float
    value: float
    fee: float
    reasoning: str
    
    def to_dict(self):
        return {
            **asdict(self),
            'timestamp': self.timestamp.isoformat()
        }

@dataclass
class Position:
    """Represents a current position in a cryptocurrency"""
    symbol: str
    quantity: float
    avg_price: float
    total_cost: float
    current_price: float
    current_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    
    def to_dict(self):
        return asdict(self)

@dataclass
class DailyReport:
    """Daily performance report"""
    date: str
    starting_balance: float
    ending_balance: float
    daily_pnl: float
    daily_pnl_pct: float
    total_pnl: float
    total_pnl_pct: float
    positions_count: int
    trades_count: int
    top_performer: Optional[str]
    worst_performer: Optional[str]
    key_actions: List[str]
    
    def to_dict(self):
        return asdict(self)

class PortfolioSimulator:
    """
    Simulates cryptocurrency trading with virtual portfolio management
    """
    
    def __init__(self, initial_balance: float = 10000.0, trading_fee: float = 0.001):
        """
        Initialize portfolio simulator
        
        Args:
            initial_balance: Starting USD balance
            trading_fee: Trading fee as decimal (0.001 = 0.1%)
        """
        self.initial_balance = float(initial_balance)
        self.current_balance = float(initial_balance)
        self.trading_fee = trading_fee
        
        # Portfolio tracking
        self.positions: Dict[str, Position] = {}
        self.trades: List[Trade] = []
        self.daily_reports: List[DailyReport] = []
        
        # Performance tracking
        self.start_date = datetime.now().date()
        self.last_report_date = None
        self.daily_snapshots = {}
        
        # File paths for persistence
        self.portfolio_file = "test_mode_portfolio.json"
        self.trades_file = "test_mode_trades.json"
        self.reports_file = "test_mode_reports.json"
        
        # Load existing data if available
        self._load_portfolio_state()
        
        logger.info(f"Portfolio Simulator initialized with ${self.initial_balance:,.2f}")
    
    def _load_portfolio_state(self):
        """Load existing portfolio state from files"""
        try:
            # Load portfolio
            if os.path.exists(self.portfolio_file):
                with open(self.portfolio_file, 'r') as f:
                    data = json.load(f)
                    self.current_balance = data.get('current_balance', self.initial_balance)
                    self.initial_balance = data.get('initial_balance', self.initial_balance)
                    self.start_date = datetime.fromisoformat(data.get('start_date', datetime.now().isoformat())).date()
                    
                    # Load positions
                    positions_data = data.get('positions', {})
                    for symbol, pos_data in positions_data.items():
                        self.positions[symbol] = Position(**pos_data)
            
            # Load trades
            if os.path.exists(self.trades_file):
                with open(self.trades_file, 'r') as f:
                    trades_data = json.load(f)
                    self.trades = [
                        Trade(**{**trade, 'timestamp': datetime.fromisoformat(trade['timestamp'])})
                        for trade in trades_data
                    ]
            
            # Load reports  
            if os.path.exists(self.reports_file):
                with open(self.reports_file, 'r') as f:
                    reports_data = json.load(f)
                    self.daily_reports = [DailyReport(**report) for report in reports_data]
                    if self.daily_reports:
                        self.last_report_date = datetime.fromisoformat(self.daily_reports[-1].date).date()
                        
        except Exception as e:
            logger.warning(f"Could not load portfolio state: {e}")
    
    def _save_portfolio_state(self):
        """Save portfolio state to files"""
        try:
            # Save portfolio
            portfolio_data = {
                'current_balance': self.current_balance,
                'initial_balance': self.initial_balance,
                'start_date': self.start_date.isoformat(),
                'positions': {symbol: pos.to_dict() for symbol, pos in self.positions.items()}
            }
            with open(self.portfolio_file, 'w') as f:
                json.dump(portfolio_data, f, indent=2)
            
            # Save trades
            with open(self.trades_file, 'w') as f:
                json.dump([trade.to_dict() for trade in self.trades], f, indent=2)
            
            # Save reports
            with open(self.reports_file, 'w') as f:
                json.dump([report.to_dict() for report in self.daily_reports], f, indent=2)
                
        except Exception as e:
            logger.error(f"Could not save portfolio state: {e}")
    
    def get_current_portfolio_value(self, current_prices: Dict[str, float]) -> float:
        """Calculate total portfolio value including cash and positions"""
        positions_value = 0.0
        
        for symbol, position in self.positions.items():
            if symbol in current_prices:
                # Update position current price and value
                position.current_price = current_prices[symbol]
                position.current_value = position.quantity * position.current_price
                position.unrealized_pnl = position.current_value - position.total_cost
                position.unrealized_pnl_pct = (position.unrealized_pnl / position.total_cost * 100) if position.total_cost > 0 else 0
                
                positions_value += position.current_value
        
        return self.current_balance + positions_value
    
    def execute_buy_order(self, symbol: str, usd_amount: float, current_price: float, reasoning: str = "") -> Optional[Trade]:
        """Execute a buy order with USD amount"""
        try:
            # Calculate fee
            fee = usd_amount * self.trading_fee
            net_amount = usd_amount - fee
            
            # Check if we have enough balance
            if self.current_balance < usd_amount:
                logger.warning(f"Insufficient balance for {symbol} buy order: ${usd_amount:.2f} > ${self.current_balance:.2f}")
                return None
            
            # Calculate quantity
            quantity = net_amount / current_price
            
            # Create trade
            trade = Trade(
                trade_id=f"BUY_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                symbol=symbol,
                side='BUY',
                quantity=quantity,
                price=current_price,
                value=usd_amount,
                fee=fee,
                reasoning=reasoning
            )
            
            # Update balance
            self.current_balance -= usd_amount
            
            # Update position
            if symbol in self.positions:
                position = self.positions[symbol]
                total_cost = position.total_cost + net_amount
                total_quantity = position.quantity + quantity
                position.avg_price = total_cost / total_quantity
                position.quantity = total_quantity
                position.total_cost = total_cost
            else:
                self.positions[symbol] = Position(
                    symbol=symbol,
                    quantity=quantity,
                    avg_price=current_price,
                    total_cost=net_amount,
                    current_price=current_price,
                    current_value=quantity * current_price,
                    unrealized_pnl=0.0,
                    unrealized_pnl_pct=0.0
                )
            
            # Record trade
            self.trades.append(trade)
            self._save_portfolio_state()
            
            logger.info(f"✅ BUY {quantity:.6f} {symbol} at ${current_price:.4f} (${usd_amount:.2f})")
            return trade
            
        except Exception as e:
            logger.error(f"Failed to execute buy order for {symbol}: {e}")
            return None
    
    def execute_sell_order(self, symbol: str, quantity: float, current_price: float, reasoning: str = "") -> Optional[Trade]:
        """Execute a sell order with quantity"""
        try:
            # Check if we have the position
            if symbol not in self.positions:
                logger.warning(f"No position in {symbol} to sell")
                return None
            
            position = self.positions[symbol]
            
            # Check if we have enough quantity
            if position.quantity < quantity:
                logger.warning(f"Insufficient {symbol} quantity: {quantity} > {position.quantity}")
                return None
            
            # Calculate proceeds
            gross_proceeds = quantity * current_price
            fee = gross_proceeds * self.trading_fee
            net_proceeds = gross_proceeds - fee
            
            # Create trade
            trade = Trade(
                trade_id=f"SELL_{symbol}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                timestamp=datetime.now(),
                symbol=symbol,
                side='SELL',
                quantity=quantity,
                price=current_price,
                value=gross_proceeds,
                fee=fee,
                reasoning=reasoning
            )
            
            # Update balance
            self.current_balance += net_proceeds
            
            # Update position
            position.quantity -= quantity
            if position.quantity <= 0.000001:  # Close position if negligible amount left
                del self.positions[symbol]
            else:
                # Proportionally reduce total cost
                position.total_cost *= (position.quantity / (position.quantity + quantity))
            
            # Record trade
            self.trades.append(trade)
            self._save_portfolio_state()
            
            logger.info(f"✅ SELL {quantity:.6f} {symbol} at ${current_price:.4f} (${gross_proceeds:.2f})")
            return trade
            
        except Exception as e:
            logger.error(f"Failed to execute sell order for {symbol}: {e}")
            return None
    
    def get_position_info(self, symbol: str) -> Optional[Position]:
        """Get current position information for a symbol"""
        return self.positions.get(symbol)
    
    def get_available_balance(self) -> float:
        """Get available USD balance for trading"""
        return self.current_balance
    
    def generate_daily_report(self, current_prices: Dict[str, float]) -> DailyReport:
        """Generate daily performance report"""
        try:
            today = datetime.now().date()
            
            # Get current portfolio value
            current_portfolio_value = self.get_current_portfolio_value(current_prices)
            
            # Get yesterday's portfolio value (or starting value for first day)
            yesterday_value = self.initial_balance
            if self.daily_reports:
                yesterday_value = self.daily_reports[-1].ending_balance
            
            # Calculate daily P&L
            daily_pnl = current_portfolio_value - yesterday_value
            daily_pnl_pct = (daily_pnl / yesterday_value * 100) if yesterday_value > 0 else 0
            
            # Calculate total P&L
            total_pnl = current_portfolio_value - self.initial_balance
            total_pnl_pct = (total_pnl / self.initial_balance * 100) if self.initial_balance > 0 else 0
            
            # Find top and worst performers
            top_performer = None
            worst_performer = None
            best_pnl = float('-inf')
            worst_pnl = float('inf')
            
            for symbol, position in self.positions.items():
                if position.unrealized_pnl_pct > best_pnl:
                    best_pnl = position.unrealized_pnl_pct
                    top_performer = f"{symbol} (+{position.unrealized_pnl_pct:.2f}%)"
                
                if position.unrealized_pnl_pct < worst_pnl:
                    worst_pnl = position.unrealized_pnl_pct
                    worst_performer = f"{symbol} ({position.unrealized_pnl_pct:.2f}%)"
            
            # Get today's trades for key actions
            today_trades = [trade for trade in self.trades if trade.timestamp.date() == today]
            key_actions = []
            
            for trade in today_trades[-5:]:  # Last 5 trades
                action = f"{trade.side} {trade.quantity:.4f} {trade.symbol} @ ${trade.price:.4f}"
                key_actions.append(action)
            
            if not key_actions:
                key_actions = ["No trades executed today"]
            
            # Create daily report
            report = DailyReport(
                date=today.isoformat(),
                starting_balance=yesterday_value,
                ending_balance=current_portfolio_value,
                daily_pnl=daily_pnl,
                daily_pnl_pct=daily_pnl_pct,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                positions_count=len(self.positions),
                trades_count=len(today_trades),
                top_performer=top_performer,
                worst_performer=worst_performer,
                key_actions=key_actions
            )
            
            # Add to reports and save
            self.daily_reports.append(report)
            self.last_report_date = today
            self._save_portfolio_state()
            
            return report
            
        except Exception as e:
            logger.error(f"Failed to generate daily report: {e}")
            return self._default_daily_report()
    
    def _default_daily_report(self) -> DailyReport:
        """Generate a default daily report on error"""
        today = datetime.now().date()
        return DailyReport(
            date=today.isoformat(),
            starting_balance=self.initial_balance,
            ending_balance=self.current_balance,
            daily_pnl=0.0,
            daily_pnl_pct=0.0,
            total_pnl=0.0,
            total_pnl_pct=0.0,
            positions_count=0,
            trades_count=0,
            top_performer=None,
            worst_performer=None,
            key_actions=["Error generating report"]
        )
    
    def should_generate_daily_report(self) -> bool:
        """Check if we should generate a daily report"""
        today = datetime.now().date()
        return self.last_report_date != today
    
    def get_portfolio_summary(self, current_prices: Dict[str, float]) -> Dict[str, Any]:
        """Get current portfolio summary"""
        current_value = self.get_current_portfolio_value(current_prices)
        total_pnl = current_value - self.initial_balance
        
        return {
            "initial_balance": self.initial_balance,
            "current_balance": self.current_balance,
            "positions_value": current_value - self.current_balance,
            "total_portfolio_value": current_value,
            "total_pnl": total_pnl,
            "total_pnl_pct": (total_pnl / self.initial_balance * 100) if self.initial_balance > 0 else 0,
            "positions": {symbol: pos.to_dict() for symbol, pos in self.positions.items()},
            "days_running": (datetime.now().date() - self.start_date).days + 1,
            "total_trades": len(self.trades)
        }
    
    def reset_portfolio(self, new_initial_balance: Optional[float] = None):
        """Reset portfolio to initial state"""
        if new_initial_balance is not None:
            self.initial_balance = float(new_initial_balance)
        
        self.current_balance = self.initial_balance
        self.positions.clear()
        self.trades.clear()
        self.daily_reports.clear()
        self.start_date = datetime.now().date()
        self.last_report_date = None
        
        # Clean up files
        for file in [self.portfolio_file, self.trades_file, self.reports_file]:
            if os.path.exists(file):
                os.remove(file)
        
        logger.info(f"Portfolio reset with ${self.initial_balance:,.2f} initial balance")
    
    def get_latest_report(self) -> Optional[DailyReport]:
        """Get the most recent daily report"""
        return self.daily_reports[-1] if self.daily_reports else None