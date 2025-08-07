#!/usr/bin/env python3
"""
Test Mode Runner with Environment Variable Fix
Ensures environment variables are properly loaded before any imports
"""
import os
import sys
from dotenv import load_dotenv

# CRITICAL: Load and force-set environment variables FIRST
print("🔧 Loading environment variables...")
load_dotenv()

# Force-set environment variables in os.environ to ensure they persist
api_key = os.getenv('OPENAI_API_KEY')
base_url = os.getenv('IONOS_BASE_URL', 'https://openai.inference.de-txl.ionos.com/v1')

if not api_key:
    print("❌ Error: OPENAI_API_KEY not found in .env file")
    sys.exit(1)

# Force-set in system environment
os.environ['OPENAI_API_KEY'] = api_key
os.environ['IONOS_BASE_URL'] = base_url

print(f"✅ Environment variables loaded:")
print(f"   OPENAI_API_KEY: {api_key[:30]}...")
print(f"   IONOS_BASE_URL: {base_url}")

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run the original script
from crypto_trader.test_mode_main import TestModeScheduler
from crypto_trader.smart_scheduler import ScheduleConfig

def main():
    print("🤖 Autonomous Crypto Trading - Test Mode Simulation (FIXED)")
    print("=" * 60)
    print("This mode simulates trading with virtual money to test strategies")
    print()
    
    # Portfolio setup
    print("💰 Portfolio Configuration:")
    try:
        initial_balance = float(input("Enter initial balance (default $10,000): ") or 10000)
    except ValueError:
        initial_balance = 10000.0
    
    try:    
        duration_days = int(input("Enter simulation duration in days (default 7): ") or 7)
    except ValueError:
        duration_days = 7
    
    print(f"   💰 Initial Balance: ${initial_balance:,.2f}")
    print(f"   📅 Duration: {duration_days} days")
    
    # Token budget setup
    print("\n🔗 Token Usage Configuration:")
    print("   1. Conservative: 100,000 tokens/day (~$10-15 estimated)")
    print("   2. Moderate: 150,000 tokens/day (~$15-25 estimated)")  
    print("   3. Aggressive: 250,000 tokens/day (~$25-40 estimated)")
    print("   4. Custom amount")
    
    try:
        token_choice = input("\nSelect token budget (1-4, default 2): ").strip() or "2"
        
        token_budgets = {
            "1": 100000,
            "2": 150000, 
            "3": 250000
        }
        
        if token_choice in token_budgets:
            max_tokens = token_budgets[token_choice]
        elif token_choice == "4":
            max_tokens = int(input("Enter daily token limit: "))
        else:
            max_tokens = 150000  # Default moderate
            
    except (ValueError, KeyboardInterrupt):
        max_tokens = 150000
    
    print(f"   🎯 Daily Token Limit: {max_tokens:,}")
    
    # Analysis frequency setup
    print("\n⏰ Analysis Frequency:")
    print("   1. Conservative: Less frequent analysis, lower token usage")
    print("   2. Balanced: Standard intervals for most scenarios")
    print("   3. Aggressive: Frequent analysis, maximum responsiveness")
    
    try:
        freq_choice = input("Select frequency (1-3, default 2): ").strip() or "2"
        
        if freq_choice == "1":  # Conservative
            config = ScheduleConfig(
                monitor_interval=10,        # 10 min monitoring
                quick_scan_interval=60,     # 1 hour quick scans  
                medium_analysis_interval=240, # 4 hour medium
                full_analysis_interval=480,   # 8 hour full
                high_volatility_threshold=0.04,
                volume_surge_threshold=0.35
            )
        elif freq_choice == "3":  # Aggressive  
            config = ScheduleConfig(
                monitor_interval=3,         # 3 min monitoring
                quick_scan_interval=20,     # 20 min quick scans
                medium_analysis_interval=90, # 1.5 hour medium  
                full_analysis_interval=240,  # 4 hour full
                high_volatility_threshold=0.02,
                volume_surge_threshold=0.20
            )
        else:  # Balanced (default)
            config = ScheduleConfig(
                monitor_interval=5,         # 5 min monitoring
                quick_scan_interval=30,     # 30 min quick scans
                medium_analysis_interval=120, # 2 hour medium
                full_analysis_interval=360,   # 6 hour full
                high_volatility_threshold=0.03,
                volume_surge_threshold=0.25
            )
    except (ValueError, KeyboardInterrupt):
        config = ScheduleConfig()  # Default balanced
    
    # Reset option
    print("\n🔄 Portfolio Reset:")
    reset_choice = input("Reset portfolio for fresh start? (y/N): ").strip().lower()
    reset_portfolio = reset_choice in ['y', 'yes']
    
    # Summary
    print("\n📊 Simulation Configuration:")
    print(f"   💰 Initial Balance: ${initial_balance:,.2f}")
    print(f"   📅 Duration: {duration_days} days")
    print(f"   🔗 Daily Token Limit: {max_tokens:,}")
    print(f"   ⏰ Monitor Interval: {config.monitor_interval} minutes")
    print(f"   ⚡ Quick Scan: {config.quick_scan_interval} minutes")
    print(f"   📊 Medium Analysis: {config.medium_analysis_interval} minutes")
    print(f"   🚀 Full Analysis: {config.full_analysis_interval} minutes")
    print(f"   🔄 Reset Portfolio: {'Yes' if reset_portfolio else 'No'}")
    
    # Confirm start
    try:
        input("\nPress Enter to start simulation (Ctrl+C to stop anytime)...")
    except KeyboardInterrupt:
        print("\nSimulation cancelled.")
        return 0
    
    try:
        # Create and run test mode scheduler
        scheduler = TestModeScheduler(
            config=config,
            initial_balance=initial_balance
        )
        
        if reset_portfolio:
            scheduler.initialize_test_crew()
            scheduler.test_crew.reset_simulation(initial_balance)
            print("✅ Portfolio reset for fresh simulation")
        
        print(f"\n🚀 Starting {duration_days}-day simulation...")
        print("📊 Real-time logs will appear below:")
        print("-" * 60)
        
        # Run simulation
        scheduler.run_test_simulation(
            max_daily_tokens=max_tokens,
            duration_days=duration_days
        )
        
    except KeyboardInterrupt:
        print("\n\n🛑 Simulation stopped by user")
        print("📊 Check the generated reports for partial results")
    except Exception as e:
        print(f"\n❌ Error during simulation: {e}")
        print("📋 Check test_mode.log for detailed error information")
        return 1
    
    print("\n🎉 Test Mode Simulation Complete!")
    print("📊 Check the generated reports and logs for detailed results")
    return 0

if __name__ == "__main__":
    exit(main())