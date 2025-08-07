# 🤖 Smart Scheduler for Autonomous Crypto Trading

The Smart Scheduler optimizes **token usage** while maintaining **effective trading analysis** by intelligently adjusting analysis frequency based on market conditions.

## 🎯 **Key Benefits**

- **💰 Token Optimization**: 70-80% reduction in token usage vs continuous mode
- **📊 Market-Responsive**: Increases analysis during volatile periods  
- **⏰ Time-Aware**: Adjusts frequency based on trading hours and weekends
- **🛡️ Risk-Managed**: Maintains safety controls and position limits
- **📈 Performance-Focused**: Full analysis when it matters most

---

## 🚀 **Quick Start**

### **Option 1: Interactive Runner** (Recommended)
```bash
python run_smart_scheduler.py
```

### **Option 2: Command Line**
```bash
PYTHONPATH=src python -m crypto_trader.smart_scheduler --max-tokens 100000
```

### **Option 3: Custom Configuration**
```bash
PYTHONPATH=src python -m crypto_trader.smart_scheduler \
    --max-tokens 50000 \
    --monitor-interval 5 \
    --quick-interval 60 \
    --medium-interval 240 \
    --full-interval 720 \
    --volatility-threshold 0.05
```

---

## 📊 **Analysis Levels**

| Level | Frequency | Tokens | Description |
|-------|-----------|--------|-------------|
| **Monitor** | 5 min | 0 | Price checks, market condition assessment |
| **Quick Scan** | 1 hour | ~2K | Light analysis (1-2 agents) |
| **Medium Analysis** | 4 hours | ~8K | Moderate analysis (3-5 agents) |
| **Full Analysis** | 12 hours | ~25K | Complete analysis (all 10 agents) |

---

## 💰 **Token Usage Presets**

### **Conservative (~$5-10/day)**
- **50,000 tokens/day**
- Focus on major market moves
- Full analysis once daily
- Weekend scaling: 1.5x intervals

### **Moderate (~$10-20/day)**
- **100,000 tokens/day** 
- Balanced monitoring and analysis
- Responsive to volatility spikes
- Recommended for most users

### **Aggressive (~$20-40/day)**
- **200,000 tokens/day**
- High-frequency analysis
- Maximum market responsiveness  
- For active trading strategies

---

## 🔥 **Smart Triggers**

The scheduler automatically triggers **intensive analysis** when:

- **📈 High Volatility**: >5% daily price moves
- **📊 Volume Surge**: >30% volume increase  
- **⚡ Flash Events**: Sudden market movements
- **🔔 Portfolio Drift**: Asset allocations exceed limits
- **📰 Market Hours**: More frequent during active periods

---

## ⚙️ **Configuration**

Edit `scheduler_config.yaml` to customize:

```yaml
# Analysis intervals (minutes)
intervals:
  monitor_only: 5
  quick_scan: 60  
  medium_analysis: 240
  full_analysis: 720

# Market thresholds
thresholds:
  high_volatility: 0.05    # 5%
  volume_surge: 0.30       # 30%
  
# Token limits  
token_limits:
  conservative: 50000
  moderate: 100000
  aggressive: 200000
```

---

## 📈 **Example Daily Schedule**

### **Moderate Mode (100K tokens)**
```
00:00 - Full Analysis (25K tokens) - Daily strategy review
04:00 - Medium Analysis (8K tokens) - Market assessment  
08:00 - Full Analysis (25K tokens) - Trading day preparation
12:00 - Medium Analysis (8K tokens) - Midday review
16:00 - Medium Analysis (8K tokens) - Afternoon check
20:00 - Medium Analysis (8K tokens) - Evening summary

Continuous: Quick scans every hour (24 × 2K = 48K tokens)
Market-triggered: Emergency analyses when needed
```

**Total**: ~146K tokens → **Scaled to 100K** through intelligent prioritization

---

## 🛡️ **Safety Features**

- **📊 Daily Token Limits**: Hard caps prevent overspending
- **⏰ Market Hours**: Reduced activity during low-volume periods
- **🔄 State Persistence**: Remembers previous analyses
- **❌ Error Recovery**: Graceful handling of API failures  
- **📈 Usage Tracking**: Detailed token consumption reports

---

## 📊 **Monitoring & Logs**

The scheduler provides real-time monitoring:

```bash
🤖 Starting Smart Scheduler for Autonomous Crypto Trading
📊 Configuration: ScheduleConfig(monitor_interval=5, quick_scan_interval=60...)
🎯 Daily token limit: 100,000

🔍 Executing quick analysis - Volatility: 2.34%
⚡ Running quick market scan...
✅ Analysis complete: quick_scan - Tokens used: 2,000
📈 Daily usage: 15,000 / 100,000 tokens

🔥 Unusual market activity detected - triggering full analysis
🚀 Running full autonomous analysis...
✅ Analysis complete: full_analysis - Tokens used: 25,000
📈 Daily usage: 40,000 / 100,000 tokens
```

---

## 🚦 **Status Indicators**

- **🟢 Monitor**: Price tracking active
- **🟡 Quick**: Light analysis running  
- **🟠 Medium**: Moderate analysis running
- **🔴 Full**: Complete analysis running
- **🔥 Triggered**: Emergency analysis activated
- **💰 Limited**: Daily token limit approached

---

## ⚡ **Performance Tips**

1. **Start Conservative**: Begin with 50K token limit
2. **Monitor Results**: Track token usage vs trading performance
3. **Adjust Thresholds**: Fine-tune volatility triggers
4. **Weekend Scaling**: Reduce frequency during low activity
5. **Market Hours**: Focus analysis during active periods

---

## 🔧 **Advanced Usage**

### **Custom Market Hours**
```python
config = ScheduleConfig(
    active_hours_start=8,    # 8 AM UTC
    active_hours_end=20,     # 8 PM UTC  
    weekend_scale_factor=2.0  # 2x intervals on weekends
)
```

### **Emergency Triggers**
```python
config = ScheduleConfig(
    high_volatility_threshold=0.03,  # 3% triggers urgent analysis
    volume_surge_threshold=0.50,     # 50% volume increase
)
```

### **Integration with Portfolio**
```python
scheduler = SmartScheduler(config)
scheduler.run_continuous(
    max_daily_tokens=100000,
    portfolio_check_interval=30  # Check positions every 30 min
)
```

---

## 📞 **Support**

For issues or questions:
- Check logs in the project directory
- Review `scheduler_config.yaml` settings
- Monitor token usage patterns
- Adjust thresholds based on market conditions

**Happy Trading! 🚀📈**