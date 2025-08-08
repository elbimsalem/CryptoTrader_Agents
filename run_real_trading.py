#!/usr/bin/env python3
"""
Real Trading Mode Runner for Autonomous Crypto Trading
CAUTION: This will execute real trades with real money
"""
import sys
import os
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from crypto_trader.autonomous_crew import AutonomousCryptoTradingCrew
from datetime import datetime
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_real_trading():
    """
    Run the autonomous trading crew in REAL TRADING MODE
    
    ⚠️  WARNING: This will execute real trades with real money!
    """
    print("🚨 REAL TRADING MODE - WARNING!")
    print("=" * 50)
    print("This mode will execute REAL trades with REAL money!")
    print("Make sure you have:")
    print("  ✅ Valid Binance API credentials")
    print("  ✅ Sufficient account balance")
    print("  ✅ Proper risk management settings")
    print("  ✅ Understanding of potential losses")
    print()
    
    # Safety check
    confirmation = input("Type 'EXECUTE REAL TRADES' to confirm you want to proceed: ")
    if confirmation != "EXECUTE REAL TRADES":
        print("❌ Real trading cancelled")
        return 1
    
    try:
        # Create autonomous crew with real trading enabled
        real_crew = AutonomousCryptoTradingCrew(
            verbose=True,
            paper_trading=False,  # ⚠️ REAL TRADING MODE
            portfolio_simulator=None  # No simulator needed for real trading
        )
        
        print("🚀 Real Trading Crew initialized")
        print("⚠️  All trades will be REAL and use REAL money!")
        
        # Create inputs
        inputs = {
            'current_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'filename_datetime': datetime.now().strftime('%Y%m%d_%H%M%S'),
            'paper_trading': False,
            'mode': 'real_trading'
        }
        
        # Validate inputs
        if real_crew.validate_inputs(inputs):
            print("✅ Input validation passed")
        
        print("🚀 Starting real trading execution...")
        print("⚠️  Monitor your account and stop if needed!")
        
        # Run the crew
        crew = real_crew.crew()
        result = crew.kickoff(inputs=inputs)
        
        print("✅ Real trading cycle completed!")
        print(f"📄 Result: {type(result)}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Real trading failed: {e}")
        logger.error(f"Real trading error: {e}", exc_info=True)
        return 1

if __name__ == "__main__":
    print("⚠️  WARNING: This script executes REAL trades!")
    print("Only run this if you understand the risks!")
    print()
    exit(run_real_trading())