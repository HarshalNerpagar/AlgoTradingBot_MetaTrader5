# Algorithmic Trading Strategy for MetaTrader 5

## 📈 Project Overview

This is an advanced algorithmic trading strategy implemented in Python, designed to execute trades on MetaTrader 5 for Forex and Cryptocurrency markets. The strategy combines multiple technical analysis approaches to generate trading signals and manage trades dynamically.

## 🚀 Key Features

- Multiple Trading Strategies:
  - TD Support Resistance (TDSR)
  - TD Breakout (TDBO)
  - TD Reversal (TDR)

- Automated Trade Management:
  - Dynamic stop-loss calculation
  - Trailing stop implementations
  - Risk management controls
  - Pending order management

- Market Compatibility:
  - Supports Forex and Cryptocurrency markets
  - Primarily tested on BTCUSD

## 🛠 Technologies Used

- Python 3.x
- MetaTrader5 API
- Pandas
- Pytz
- Custom Technical Analysis Modules

## 📊 Strategy Components

### 1. TD Support Resistance (TDSR)
- Identifies key support and resistance levels
- Generates long and short trade signals based on price action

### 2. TD Breakout (TDBO)
- Detects potential breakout opportunities
- Creates trade entries at significant price levels

### 3. TD Reversal (TDR)
- Identifies potential trend reversal points
- Generates contrarian trade signals

## 🔧 Configuration Parameters

Key configurable parameters in the `TradingStrategy` class:

- `MULTIPLAYER`: Risk multiplier (default: 1.5)
- `RISK_TO_REWARD`: Reward-to-risk ratio (default: 5)
- `BREAK_EVEN_POINT`: Threshold for break-even stop loss (default: 0.3)

## 🛡️ Risk Management

- Adaptive stop-loss calculation
- Trailing stop implementation
- Position sizing based on Average True Range (ATR)
- Limit on consecutive trade attempts

## 📦 Installation

### Prerequisites
- Python 3.8+
- MetaTrader 5 Terminal
- Required Python packages:
  ```bash
  pip install MetaTrader5 pandas pytz
  ```

### Setup
1. Clone the repository
2. Install dependencies
3. Configure MetaTrader 5 connection details
4. Adjust strategy parameters as needed

## 🚦 Usage

```python
strategy = TradingStrategy()
strategy.connect()
```

## ⚠️ Disclaimers

- This is an experimental trading strategy
- Past performance does not guarantee future results
- Use at your own risk
- Always test in a demo environment first

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request


## Contact
For internship inquiries or questions about the project, please reach out through:
- LinkedIn: https://www.linkedin.com/in/harshal-nerpagar/
- Email: harshal.j23csai@nst.rishihood.edu.in
- GitHub: https://github.com/HarshalNerpagar
