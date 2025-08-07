"""
Test Mode Main Runner for Extended Autonomous Trading Simulation
Combines intelligent scheduling with portfolio simulation for comprehensive testing
"""
import os
import sys
import argparse
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import test mode components
from .test_mode_crew import TestModeCryptoTradingCrew, run_test_mode_crew
from .portfolio_simulator import PortfolioSimulator, DailyReport
from .smart_scheduler import SmartScheduler, ScheduleConfig, AnalysisLevel

# Configure logging
os.makedirs('output', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join('output', 'test_mode.log')),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("crypto_trader.test_mode_main")

class TestModeScheduler(SmartScheduler):
    """
    Enhanced scheduler for test mode with portfolio simulation integration
    """
    
    def __init__(self, config: Optional[ScheduleConfig] = None, initial_balance: float = 10000.0):
        super().__init__(config)
        self.initial_balance = initial_balance
        self.test_crew = None
        self.daily_reports = []
        
    def initialize_test_crew(self):
        """Initialize the test mode crew"""
        if not self.test_crew:
            self.test_crew = TestModeCryptoTradingCrew(
                initial_balance=self.initial_balance,
                verbose=True
            )
            logger.info(f"Test mode crew initialized with ${self.initial_balance:,.2f}")
    
    def execute_test_analysis(self, level: AnalysisLevel, market_condition) -> Dict[str, Any]:
        """Execute test mode analysis with portfolio simulation"""
        logger.info(f"🔍 Executing {level.value} test analysis - Volatility: {market_condition.volatility_24h:.2%}")
        
        result = {"level": level.value, "timestamp": datetime.now().isoformat()}
        
        try:
            self.initialize_test_crew()
            
            if level == AnalysisLevel.MONITOR_ONLY:
                # Just monitor portfolio and market conditions
                current_prices = self._get_current_prices()
                portfolio_summary = self.test_crew.get_portfolio_summary(current_prices)
                
                result.update({
                    "action": "monitor",
                    "portfolio_value": portfolio_summary["total_portfolio_value"],
                    "daily_pnl": portfolio_summary["total_pnl"],
                    "positions": len(portfolio_summary["positions"]),
                    "market_condition": market_condition.__dict__,
                    "tokens_used": 0
                })
                self.analysis_count["monitor"] += 1
                
            elif level in [AnalysisLevel.QUICK_SCAN, AnalysisLevel.MEDIUM_ANALYSIS, AnalysisLevel.FULL_ANALYSIS]:
                # Run full test mode crew analysis
                inputs = {
                    'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'filename_datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
                    'initial_balance': self.initial_balance,
                    'test_mode': True
                }
                
                crew_result = self.test_crew.crew().kickoff(inputs=inputs)
                
                # Get updated portfolio summary
                current_prices = self._get_current_prices()
                portfolio_summary = self.test_crew.get_portfolio_summary(current_prices)
                
                # Generate daily report if needed
                daily_report = None
                if self.test_crew.should_generate_daily_report():
                    daily_report = self.test_crew.generate_daily_report(current_prices)
                    self.daily_reports.append(daily_report)
                    logger.info(f"📊 Daily report generated: {daily_report.daily_pnl:+.2f} ({daily_report.daily_pnl_pct:+.2f}%)")
                
                # Estimate token usage based on level
                token_usage = {
                    AnalysisLevel.QUICK_SCAN: 5000,
                    AnalysisLevel.MEDIUM_ANALYSIS: 15000,
                    AnalysisLevel.FULL_ANALYSIS: 35000  # Higher due to additional agents
                }[level]
                
                result.update({
                    "action": level.value,
                    "crew_result": str(crew_result)[:1000] + "..." if len(str(crew_result)) > 1000 else str(crew_result),
                    "portfolio_summary": portfolio_summary,
                    "daily_report": daily_report.to_dict() if daily_report else None,
                    "simulation_stats": self.test_crew.get_simulation_stats(),
                    "tokens_used": token_usage
                })
                
                self.token_usage_today += token_usage
                self.analysis_count[level.value.split('_')[0]] += 1
        
        except Exception as e:
            logger.error(f"Test analysis failed: {e}")
            result["error"] = str(e)
        
        # Update last analysis time
        self.last_analysis[level.value] = datetime.now()
        return result
    
    def _get_current_prices(self) -> Dict[str, float]:
        """Get current prices for portfolio valuation"""
        try:
            if self.test_crew and self.test_crew.portfolio_simulator.positions:
                symbols = list(self.test_crew.portfolio_simulator.positions.keys())
                
                # Get prices from Binance for held positions
                prices = {}
                for symbol in symbols:
                    try:
                        result = self.binance_tool._run("get_ticker_24hr", {"symbol": symbol})
                        data = json.loads(result)
                        if "lastPrice" in data:
                            prices[symbol] = float(data["lastPrice"])
                    except Exception as e:
                        logger.warning(f"Could not get price for {symbol}: {e}")
                
                return prices
        except Exception as e:
            logger.warning(f"Could not get current prices: {e}")
        
        return {}
    
    def run_test_simulation(self, max_daily_tokens: int = 150000, duration_days: int = 30):
        """
        Run extended test simulation
        
        Args:
            max_daily_tokens: Maximum tokens per day (higher for test mode)
            duration_days: How many days to run simulation
        """
        logger.info(f"🚀 Starting Test Mode Simulation")
        logger.info(f"💰 Initial Balance: ${self.initial_balance:,.2f}")
        logger.info(f"🎯 Daily Token Limit: {max_daily_tokens:,}")
        logger.info(f"📅 Simulation Duration: {duration_days} days")
        logger.info(f"📊 Configuration: {self.config}")
        
        start_time = datetime.now()
        end_time = start_time + timedelta(days=duration_days)
        simulation_day = 1
        
        while datetime.now() < end_time:
            try:
                current_time = datetime.now()
                
                # Reset daily token counter at midnight
                if current_time.hour == 0 and current_time.minute < 10:
                    self.token_usage_today = 0
                    logger.info(f"🔄 Day {simulation_day} started - Token counter reset")
                    simulation_day += 1
                
                # Check daily token limit
                if self.token_usage_today >= max_daily_tokens:
                    logger.warning(f"💰 Daily token limit reached ({max_daily_tokens:,}). Monitoring only.")
                    time.sleep(self.config.monitor_interval * 60)
                    continue
                
                # Assess market conditions
                market_condition = self.get_market_conditions()
                
                # Determine analysis level
                analysis_level = self.determine_analysis_level(market_condition)
                
                # Execute test analysis
                result = self.execute_test_analysis(analysis_level, market_condition)
                
                # Log results
                if analysis_level != AnalysisLevel.MONITOR_ONLY:
                    logger.info(f"✅ Test analysis complete: {result.get('action')}")
                    logger.info(f"💰 Portfolio Value: ${result.get('portfolio_summary', {}).get('total_portfolio_value', 0):,.2f}")
                    logger.info(f"📈 Total P&L: {result.get('portfolio_summary', {}).get('total_pnl_pct', 0):+.2f}%")
                    logger.info(f"🔗 Tokens used: {result.get('tokens_used', 0)} | Daily: {self.token_usage_today:,}/{max_daily_tokens:,}")
                
                # Generate detailed report every hour
                if current_time.minute == 0:
                    self._log_simulation_summary()
                
                # Sleep until next check
                sleep_time = self.config.monitor_interval * 60
                logger.debug(f"😴 Sleeping for {sleep_time/60:.1f} minutes...")
                time.sleep(sleep_time)
                
            except KeyboardInterrupt:
                logger.info("🛑 Test simulation stopped by user")
                self._generate_final_report()
                break
            except Exception as e:
                logger.error(f"❌ Unexpected error in test simulation: {e}")
                time.sleep(60)  # Wait 1 minute before retry
        
        # Simulation completed
        logger.info("✅ Test simulation completed!")
        self._generate_final_report()
    
    def _log_simulation_summary(self):
        """Log hourly simulation summary"""
        if self.test_crew:
            try:
                current_prices = self._get_current_prices()
                portfolio_summary = self.test_crew.get_portfolio_summary(current_prices)
                simulation_stats = self.test_crew.get_simulation_stats()
                
                logger.info("📊 SIMULATION SUMMARY:")
                logger.info(f"   💰 Portfolio Value: ${portfolio_summary['total_portfolio_value']:,.2f}")
                logger.info(f"   📈 Total P&L: {portfolio_summary['total_pnl']:+,.2f} ({portfolio_summary['total_pnl_pct']:+.2f}%)")
                logger.info(f"   🏦 Cash Balance: ${portfolio_summary['current_balance']:,.2f}")
                logger.info(f"   📊 Positions: {len(portfolio_summary['positions'])}")
                logger.info(f"   📈 Total Trades: {simulation_stats['total_trades']}")
                logger.info(f"   📅 Days Running: {simulation_stats['days_running']}")
                logger.info(f"   🔗 Token Usage: {self.token_usage_today:,}")
                
            except Exception as e:
                logger.warning(f"Could not log simulation summary: {e}")
    
    def _generate_final_report(self):
        """Generate comprehensive final simulation report"""
        try:
            if not self.test_crew:
                logger.warning("No test crew available for final report")
                return
            
            current_prices = self._get_current_prices()
            portfolio_summary = self.test_crew.get_portfolio_summary(current_prices)
            simulation_stats = self.test_crew.get_simulation_stats()
            
            # Calculate additional metrics
            total_return_pct = portfolio_summary['total_pnl_pct']
            days_running = simulation_stats['days_running']
            annualized_return = (total_return_pct / days_running * 365) if days_running > 0 else 0
            
            final_report = {
                "simulation_summary": {
                    "initial_balance": self.initial_balance,
                    "final_balance": portfolio_summary['total_portfolio_value'],
                    "total_pnl": portfolio_summary['total_pnl'],
                    "total_return_pct": total_return_pct,
                    "annualized_return_pct": annualized_return,
                    "days_running": days_running,
                    "total_trades": simulation_stats['total_trades']
                },
                "portfolio_breakdown": portfolio_summary,
                "daily_reports_count": len(self.daily_reports),
                "token_usage": {
                    "total_estimated": sum(self.analysis_count[k] * v for k, v in {
                        "quick": 5000, "medium": 15000, "full": 35000, "monitor": 0
                    }.items()),
                    "analysis_breakdown": self.analysis_count
                }
            }
            
            # Ensure output directory exists
            output_dir = "output"
            os.makedirs(output_dir, exist_ok=True)
            
            # Save final report in output folder
            report_filename = f"test_simulation_final_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            report_filepath = os.path.join(output_dir, report_filename)
            with open(report_filepath, 'w') as f:
                json.dump(final_report, f, indent=2, default=str)
            
            logger.info("🎉 FINAL SIMULATION REPORT:")
            logger.info(f"   💰 Initial: ${self.initial_balance:,.2f}")
            logger.info(f"   💰 Final: ${portfolio_summary['total_portfolio_value']:,.2f}")
            logger.info(f"   📈 Total Return: {total_return_pct:+.2f}%")
            logger.info(f"   📊 Annualized: {annualized_return:+.2f}%")
            logger.info(f"   📅 Duration: {days_running} days")
            logger.info(f"   📈 Total Trades: {simulation_stats['total_trades']}")
            logger.info(f"   📋 Report saved: {report_filepath}")
            
        except Exception as e:
            logger.error(f"Failed to generate final report: {e}")

def main():
    """Main entry point for test mode simulation"""
    parser = argparse.ArgumentParser(description="Test Mode Autonomous Crypto Trading Simulation")
    
    # Portfolio simulation parameters
    parser.add_argument("--initial-balance", type=float, default=10000.0, help="Initial portfolio balance in USD")
    parser.add_argument("--duration-days", type=int, default=7, help="Simulation duration in days")
    
    # Token management
    parser.add_argument("--max-tokens", type=int, default=150000, help="Maximum daily token usage")
    
    # Scheduling parameters
    parser.add_argument("--monitor-interval", type=int, default=5, help="Monitor interval in minutes")
    parser.add_argument("--quick-interval", type=int, default=30, help="Quick analysis interval in minutes")
    parser.add_argument("--medium-interval", type=int, default=120, help="Medium analysis interval in minutes")
    parser.add_argument("--full-interval", type=int, default=360, help="Full analysis interval in minutes")
    
    # Market condition thresholds
    parser.add_argument("--volatility-threshold", type=float, default=0.03, help="Volatility threshold for urgent analysis")
    parser.add_argument("--volume-threshold", type=float, default=0.25, help="Volume surge threshold")
    
    # Control options
    parser.add_argument("--reset-portfolio", action="store_true", help="Reset portfolio before starting")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    try:
        # Create scheduler configuration
        config = ScheduleConfig(
            monitor_interval=args.monitor_interval,
            quick_scan_interval=args.quick_interval,
            medium_analysis_interval=args.medium_interval,
            full_analysis_interval=args.full_interval,
            high_volatility_threshold=args.volatility_threshold,
            volume_surge_threshold=args.volume_threshold
        )
        
        # Create test mode scheduler
        scheduler = TestModeScheduler(
            config=config,
            initial_balance=args.initial_balance
        )
        
        # Reset portfolio if requested
        if args.reset_portfolio:
            scheduler.initialize_test_crew()
            scheduler.test_crew.reset_simulation(args.initial_balance)
            logger.info("Portfolio reset for fresh simulation")
        
        # Run simulation
        scheduler.run_test_simulation(
            max_daily_tokens=args.max_tokens,
            duration_days=args.duration_days
        )
        
    except KeyboardInterrupt:
        logger.info("🛑 Test mode simulation stopped by user")
    except Exception as e:
        logger.error(f"❌ Error in test mode simulation: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())