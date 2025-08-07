"""
Smart Scheduler for Autonomous Cryptocurrency Trading
Optimizes token usage while maintaining effective trading analysis
"""
import os
import time
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Import trading components
from .tools.binance_direct_tool import BinanceDirectTool
from .autonomous_main import run_autonomous_crew

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crypto_trader.smart_scheduler")

class AnalysisLevel(Enum):
    """Different levels of analysis with varying token consumption"""
    MONITOR_ONLY = "monitor"      # 0 tokens - just price checks
    QUICK_SCAN = "quick"          # ~2K tokens - 1 agent
    MEDIUM_ANALYSIS = "medium"    # ~8K tokens - 3 agents  
    FULL_ANALYSIS = "full"        # ~25K tokens - all 10 agents

@dataclass
class MarketCondition:
    """Market condition assessment"""
    volatility_24h: float
    volume_change: float
    price_change: float
    unusual_activity: bool
    timestamp: datetime

@dataclass
class ScheduleConfig:
    """Configuration for smart scheduling"""
    # Interval settings (in minutes)
    monitor_interval: int = 5        # Price monitoring
    quick_scan_interval: int = 60    # Light analysis
    medium_analysis_interval: int = 240  # 4 hours
    full_analysis_interval: int = 720    # 12 hours
    
    # Market condition thresholds
    high_volatility_threshold: float = 0.05  # 5%
    volume_surge_threshold: float = 0.30     # 30% volume increase
    significant_price_change: float = 0.03   # 3% price change
    
    # Trading hours (24/7 for crypto but can optimize)
    active_hours_start: int = 6   # 6 AM UTC
    active_hours_end: int = 22    # 10 PM UTC
    
    # Weekend scaling factor
    weekend_scale_factor: float = 1.5  # 1.5x intervals on weekends

class SmartScheduler:
    """
    Intelligent scheduler that optimizes trading analysis frequency
    based on market conditions and token efficiency
    """
    
    def __init__(self, config: Optional[ScheduleConfig] = None):
        self.config = config or ScheduleConfig()
        self.binance_tool = BinanceDirectTool()
        self.last_analysis = {}
        self.market_state_file = "market_state.json"
        self.token_usage_file = "token_usage.json"
        
        # Initialize tracking
        self.token_usage_today = 0
        self.analysis_count = {"monitor": 0, "quick": 0, "medium": 0, "full": 0}
        
    def load_previous_state(self) -> Dict[str, Any]:
        """Load previous market state for comparison"""
        try:
            if os.path.exists(self.market_state_file):
                with open(self.market_state_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Could not load previous state: {e}")
        return {}
    
    def save_market_state(self, state: Dict[str, Any]):
        """Save current market state"""
        try:
            with open(self.market_state_file, 'w') as f:
                json.dump(state, f, default=str)
        except Exception as e:
            logger.warning(f"Could not save market state: {e}")
    
    def get_market_conditions(self) -> MarketCondition:
        """Assess current market conditions"""
        try:
            # Get top symbols for market overview
            result = self.binance_tool._run("get_top_symbols", {"limit": 10})
            data = json.loads(result)
            
            if "error" in data:
                logger.error(f"Binance API error: {data['error']}")
                return self._default_market_condition()
            
            # Calculate aggregate market metrics
            symbols = data.get("top_symbols", [])
            if not symbols:
                return self._default_market_condition()
            
            # Calculate volatility and volume metrics
            volatilities = []
            volume_changes = []
            price_changes = []
            
            for symbol in symbols[:5]:  # Top 5 for efficiency
                volatility = abs(symbol.get("change_24h", 0)) / 100
                volatilities.append(volatility)
                price_changes.append(symbol.get("change_24h", 0) / 100)
                
                # Volume change would need historical comparison
                # For now, use volume as proxy for activity
                volume_24h = symbol.get("volume_24h", 0)
                volume_changes.append(volume_24h)
            
            avg_volatility = sum(volatilities) / len(volatilities) if volatilities else 0
            avg_price_change = sum(price_changes) / len(price_changes) if price_changes else 0
            total_volume = sum(volume_changes)
            
            # Load previous state for comparison
            prev_state = self.load_previous_state()
            prev_volume = prev_state.get("total_volume", total_volume)
            volume_change_pct = (total_volume - prev_volume) / prev_volume if prev_volume else 0
            
            # Detect unusual activity
            unusual_activity = (
                avg_volatility > self.config.high_volatility_threshold or
                abs(volume_change_pct) > self.config.volume_surge_threshold or
                abs(avg_price_change) > self.config.significant_price_change
            )
            
            condition = MarketCondition(
                volatility_24h=avg_volatility,
                volume_change=volume_change_pct,
                price_change=avg_price_change,
                unusual_activity=unusual_activity,
                timestamp=datetime.now()
            )
            
            # Save current state
            self.save_market_state({
                "total_volume": total_volume,
                "avg_volatility": avg_volatility,
                "timestamp": datetime.now().isoformat(),
                "symbols": symbols[:5]
            })
            
            return condition
            
        except Exception as e:
            logger.error(f"Error assessing market conditions: {e}")
            return self._default_market_condition()
    
    def _default_market_condition(self) -> MarketCondition:
        """Return default market condition on error"""
        return MarketCondition(
            volatility_24h=0.02,
            volume_change=0.0,
            price_change=0.0,
            unusual_activity=False,
            timestamp=datetime.now()
        )
    
    def determine_analysis_level(self, market_condition: MarketCondition) -> AnalysisLevel:
        """Determine appropriate analysis level based on market conditions"""
        now = datetime.now()
        
        # Check if unusual market activity detected
        if market_condition.unusual_activity:
            logger.info("🔥 Unusual market activity detected - triggering full analysis")
            return AnalysisLevel.FULL_ANALYSIS
        
        # Check time-based rules
        is_weekend = now.weekday() >= 5
        is_active_hours = self.config.active_hours_start <= now.hour <= self.config.active_hours_end
        
        # Get last analysis times
        last_full = self.last_analysis.get("full", datetime.min)
        last_medium = self.last_analysis.get("medium", datetime.min)
        last_quick = self.last_analysis.get("quick", datetime.min)
        
        # Calculate intervals (scale for weekends)
        scale = self.config.weekend_scale_factor if is_weekend else 1.0
        
        full_interval = timedelta(minutes=self.config.full_analysis_interval * scale)
        medium_interval = timedelta(minutes=self.config.medium_analysis_interval * scale)
        quick_interval = timedelta(minutes=self.config.quick_scan_interval * scale)
        
        # Determine analysis level
        if now - last_full >= full_interval:
            return AnalysisLevel.FULL_ANALYSIS
        elif now - last_medium >= medium_interval and is_active_hours:
            return AnalysisLevel.MEDIUM_ANALYSIS
        elif now - last_quick >= quick_interval:
            return AnalysisLevel.QUICK_SCAN
        else:
            return AnalysisLevel.MONITOR_ONLY
    
    def execute_analysis(self, level: AnalysisLevel, market_condition: MarketCondition) -> Dict[str, Any]:
        """Execute the appropriate level of analysis"""
        logger.info(f"🔍 Executing {level.value} analysis - Volatility: {market_condition.volatility_24h:.2%}")
        
        result = {"level": level.value, "timestamp": datetime.now().isoformat()}
        
        if level == AnalysisLevel.MONITOR_ONLY:
            # Just log market condition, no token usage
            result.update({
                "action": "monitor",
                "market_condition": market_condition.__dict__,
                "tokens_used": 0
            })
            self.analysis_count["monitor"] += 1
            
        elif level == AnalysisLevel.QUICK_SCAN:
            # Run lightweight analysis (could be just market scanner)
            logger.info("⚡ Running quick market scan...")
            try:
                # For now, run full analysis but could be optimized to single agent
                crew_result = run_autonomous_crew(verbose=False)
                result.update({
                    "action": "quick_scan",
                    "crew_result": str(crew_result)[:500] + "..." if len(str(crew_result)) > 500 else str(crew_result),
                    "tokens_used": 2000  # Estimated
                })
                self.token_usage_today += 2000
                self.analysis_count["quick"] += 1
            except Exception as e:
                logger.error(f"Quick scan failed: {e}")
                result["error"] = str(e)
        
        elif level == AnalysisLevel.MEDIUM_ANALYSIS:
            # Run medium analysis (3-5 agents)
            logger.info("📊 Running medium market analysis...")
            try:
                crew_result = run_autonomous_crew(verbose=False)
                result.update({
                    "action": "medium_analysis", 
                    "crew_result": str(crew_result)[:1000] + "..." if len(str(crew_result)) > 1000 else str(crew_result),
                    "tokens_used": 8000  # Estimated
                })
                self.token_usage_today += 8000
                self.analysis_count["medium"] += 1
            except Exception as e:
                logger.error(f"Medium analysis failed: {e}")
                result["error"] = str(e)
        
        elif level == AnalysisLevel.FULL_ANALYSIS:
            # Run complete analysis (all 10 agents)
            logger.info("🚀 Running full autonomous analysis...")
            try:
                crew_result = run_autonomous_crew(verbose=True)
                result.update({
                    "action": "full_analysis",
                    "crew_result": crew_result,
                    "tokens_used": 25000  # Estimated
                })
                self.token_usage_today += 25000
                self.analysis_count["full"] += 1
            except Exception as e:
                logger.error(f"Full analysis failed: {e}")
                result["error"] = str(e)
        
        # Update last analysis time
        self.last_analysis[level.value] = datetime.now()
        
        return result
    
    def run_continuous(self, max_daily_tokens: int = 100000):
        """
        Run continuous smart scheduling
        
        Args:
            max_daily_tokens: Maximum tokens to use per day
        """
        logger.info("🤖 Starting Smart Scheduler for Autonomous Crypto Trading")
        logger.info(f"📊 Configuration: {self.config}")
        logger.info(f"🎯 Daily token limit: {max_daily_tokens:,}")
        
        while True:
            try:
                # Check daily token limit
                if self.token_usage_today >= max_daily_tokens:
                    logger.warning(f"💰 Daily token limit ({max_daily_tokens:,}) reached. Monitoring only.")
                    time.sleep(self.config.monitor_interval * 60)
                    continue
                
                # Assess market conditions
                market_condition = self.get_market_conditions()
                
                # Determine analysis level
                analysis_level = self.determine_analysis_level(market_condition)
                
                # Execute analysis
                result = self.execute_analysis(analysis_level, market_condition)
                
                # Log results
                if analysis_level != AnalysisLevel.MONITOR_ONLY:
                    logger.info(f"✅ Analysis complete: {result.get('action')} - Tokens used: {result.get('tokens_used', 0)}")
                    logger.info(f"📈 Daily usage: {self.token_usage_today:,} / {max_daily_tokens:,} tokens")
                
                # Log daily summary periodically
                if datetime.now().minute == 0:  # Every hour
                    self._log_daily_summary()
                
                # Wait until next check
                sleep_time = self.config.monitor_interval * 60
                logger.debug(f"😴 Sleeping for {sleep_time/60:.1f} minutes...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Smart Scheduler stopped by user")
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in scheduler: {e}")
                time.sleep(60)  # Wait 1 minute before retry
    
    def _log_daily_summary(self):
        """Log daily summary statistics"""
        logger.info("📊 DAILY SUMMARY:")
        logger.info(f"   💰 Tokens used: {self.token_usage_today:,}")
        logger.info(f"   📈 Analysis count: {self.analysis_count}")
        
        # Reset daily counters at midnight
        if datetime.now().hour == 0 and datetime.now().minute == 0:
            self.token_usage_today = 0
            self.analysis_count = {"monitor": 0, "quick": 0, "medium": 0, "full": 0}
            logger.info("🔄 Daily counters reset")

def main():
    """Main entry point for smart scheduler"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Smart Scheduler for Autonomous Crypto Trading")
    parser.add_argument("--max-tokens", type=int, default=100000, help="Maximum daily token usage")
    parser.add_argument("--monitor-interval", type=int, default=5, help="Monitor interval in minutes")
    parser.add_argument("--quick-interval", type=int, default=60, help="Quick scan interval in minutes")
    parser.add_argument("--medium-interval", type=int, default=240, help="Medium analysis interval in minutes")
    parser.add_argument("--full-interval", type=int, default=720, help="Full analysis interval in minutes")
    parser.add_argument("--volatility-threshold", type=float, default=0.05, help="Volatility threshold for urgent analysis")
    
    args = parser.parse_args()
    
    # Create configuration
    config = ScheduleConfig(
        monitor_interval=args.monitor_interval,
        quick_scan_interval=args.quick_interval,
        medium_analysis_interval=args.medium_interval,
        full_analysis_interval=args.full_interval,
        high_volatility_threshold=args.volatility_threshold
    )
    
    # Create and run scheduler
    scheduler = SmartScheduler(config)
    scheduler.run_continuous(max_daily_tokens=args.max_tokens)

if __name__ == "__main__":
    main()