#!/usr/bin/env python3
"""
Extended Test Mode - Quick Launcher
Run autonomous trading with comprehensive virtual simulation and reporting
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crypto_trader.test_mode_crew import TestModeCryptoTradingCrew
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_extended_test(initial_balance=10000.0, verbose=True):
    """
    Run Extended Test Mode with comprehensive reporting
    
    Args:
        initial_balance: Starting virtual portfolio balance
        verbose: Enable detailed logging
    """
    print("🚀 Extended Test Mode - Autonomous Trading Simulation")
    print("=" * 60)
    print("Features:")
    print("  ✅ Virtual portfolio simulation")
    print("  ✅ Comprehensive market analysis")
    print("  ✅ Risk management and trade execution")
    print("  ✅ Daily performance reporting")
    print("  ✅ Benchmark comparisons")
    print("  ✅ Trade logging and audit trails")
    print()
    
    try:
        print(f"💰 Initializing with ${initial_balance:,.2f} virtual balance...")
        
        # Create extended test mode crew
        test_crew = TestModeCryptoTradingCrew(
            initial_balance=initial_balance,
            verbose=verbose
        )
        
        print(f"✅ Extended test crew initialized")
        print(f"📊 Agents: {len(test_crew.crew().agents)}")
        print(f"📋 Tasks: {len(test_crew.crew().tasks)}")
        
        # Show portfolio status
        portfolio_summary = test_crew.get_portfolio_summary({})
        print(f"💰 Starting Balance: ${portfolio_summary.get('current_balance', 0):,.2f}")
        print()
        
        # Create inputs
        inputs = {
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename_datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'initial_balance': initial_balance,
            'test_mode': True
        }
        
        print("🚀 Starting extended test execution...")
        print("📊 This includes full market analysis, strategy development, and virtual trading")
        print("⏱️  This may take several minutes to complete all agent tasks")
        print()
        
        # Run the extended test
        crew = test_crew.crew()
        result = crew.kickoff(inputs=inputs)
        
        print("\n✅ Extended test execution completed!")
        
        # Show final portfolio status
        final_summary = test_crew.get_portfolio_summary({})
        print("\n📊 Final Portfolio Status:")
        print(f"   💰 Final Balance: ${final_summary.get('current_balance', 0):,.2f}")
        print(f"   📊 Total Value: ${final_summary.get('total_value', 0):,.2f}")
        print(f"   📈 Active Positions: {len(final_summary.get('positions', []))}")
        print(f"   🔄 Total Trades: {final_summary.get('total_trades', 0)}")
        
        # Show P&L
        initial_value = initial_balance
        final_value = final_summary.get('total_value', initial_balance)
        pnl = final_value - initial_value
        pnl_pct = (pnl / initial_value * 100) if initial_value > 0 else 0
        
        print(f"   📈 P&L: ${pnl:+,.2f} ({pnl_pct:+.2f}%)")
        
        # Check for reports
        print(f"\n📄 Check the 'output/' directory for:")
        print(f"   • Trading strategy reports (.md files)")
        print(f"   • Simulation final reports (.json files)")
        print(f"   • Daily performance reports")
        
        return 0
        
    except KeyboardInterrupt:
        print(f"\n⚠️ Extended test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n❌ Extended test failed: {e}")
        logger.error(f"Extended test error: {e}", exc_info=True)
        return 1

def main():
    """Main launcher with optional customization"""
    print("🔧 Configuration Options:")
    
    try:
        balance_input = input("Enter initial balance (default $10,000): ").strip()
        initial_balance = float(balance_input) if balance_input else 10000.0
    except ValueError:
        initial_balance = 10000.0
    
    verbose_input = input("Enable verbose logging? (y/N): ").strip().lower()
    verbose = verbose_input in ['y', 'yes']
    
    print()
    return run_extended_test(initial_balance=initial_balance, verbose=verbose)

if __name__ == "__main__":
    exit(main())