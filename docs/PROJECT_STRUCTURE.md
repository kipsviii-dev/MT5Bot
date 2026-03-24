# MT5 Live Trading Bot - Project Structure

## ð Directory Organization

```
mt5_live_trading_bot/
|
|-- ð src/                              # Core source code
|   |-- mt5_live_trading_connector.py    # MT5 connection manager
|   |-- sunrise_signal_adapter.py        # Strategy signal adapter
|   |-- sunrise_signal_adapter.pyi       # Type hints
|   `-- __init__.py                      # Package initialization
|
|-- ð strategies/                       # Trading strategies
|   |-- kips_strategy_audusd.py          # AUD/USD strategy
|   |-- kips_strategy_eurusd.py          # EUR/USD strategy
|   |-- kips_strategy_gbpusd.py          # GBP/USD strategy
|   |-- kips_strategy_usdchf.py          # USD/CHF strategy
|   |-- kips_strategy_xagusd.py          # XAG/USD strategy (Silver)
|   |-- kips_strategy_xauusd.py          # XAU/USD strategy (Gold)
|   `-- __init__.py                      # Strategies package
|
|-- ð testing/                          # Test files
|   |-- deep_stress_test.py             # Comprehensive system test
|   |-- test_monitor_components.py       # Component unit tests
|   |-- test_setup.py                   # Setup validation tests
|   `-- test_signal_detection.py        # Signal detection tests
|
|-- ð docs/                             # Documentation
|   |-- ADVANCED_GUI_COMPLETE.md        # Advanced GUI documentation
|   |-- DEEP_TEST_RESULTS.md            # Test results documentation
|   |-- README.md                       # Original README
|   `-- README_NEW.md                   # Updated README
|
|-- ð config/                           # Configuration files
|   `-- (strategy configuration files)
|
|-- ð logs/                             # Log files
|   `-- (application logs)
|
|-- ð .vscode/                          # VS Code settings
|   |-- settings.json                   # Python interpreter & settings
|   `-- launch.json                     # Debug configurations
|
|-- ð venv/                             # Virtual environment
|   `-- (Python virtual environment)
|
|-- ð§ Main Application Files
|   |-- advanced_mt5_monitor_gui.py     # Advanced monitoring GUI [star]
|   |-- basic_mt5_monitor_gui.py        # Basic monitoring GUI
|   |-- launch_advanced_monitor.py      # Professional launcher [star]
|   `-- start_advanced_monitor.py       # Simple launcher
|
|-- ð Configuration & Setup
|   |-- requirements.txt                # Python dependencies [ok]
|   |-- pyproject.toml                  # Project metadata
|   |-- setup.ps1                      # PowerShell setup script
|   |-- .gitignore                      # Git ignore rules
|   `-- PROJECT_STRUCTURE.md            # This file
|
`-- ð Documentation
    `-- README.md                       # Main project README
```

## ð Quick Start

### 1. Environment Setup
```powershell
# Navigate to project directory
cd "c:\IvÃ¡n\Yosoybuendesarrollador\Python\Portafolio\mt5_live_trading_bot"

# Install dependencies
pip install -r requirements.txt
```

### 2. Launch Advanced Monitor
```powershell
# Professional launcher with dependency checks
python launch_advanced_monitor.py

# OR simple launcher
python start_advanced_monitor.py
```

### 3. Run Tests
```powershell
# Navigate to testing directory
cd testing

# Run comprehensive tests
python deep_stress_test.py

# Run component tests
python test_monitor_components.py
```

## â¨ Key Features

### ð¯ Advanced Monitor GUI (`advanced_mt5_monitor_gui.py`)
- **Strategy Phase Tracking**: NORMAL -> PULLBACK -> BREAKOUT
- **Asset-Specific EMA Configurations**: Dynamic parameter loading
- **Professional Candlestick Charts**: mplfinance integration
- **Real-Time Indicator Display**: EMA, RSI, MACD with live updates
- **Multi-Asset Support**: 6 major currency pairs + precious metals

### ð Professional Launcher (`launch_advanced_monitor.py`)
- **Dependency Validation**: Automatic package installation
- **Dynamic Imports**: Resolves VS Code import warnings
- **Error Handling**: Graceful degradation and user feedback
- **VS Code Integration**: Optimized for development environment

### ð Core Components
- **MT5 Connector**: Reliable MetaTrader 5 integration
- **Signal Adapter**: Strategy-specific parameter management
- **Strategy Suite**: Complete trading strategies for 6+ assets
- **Test Suite**: Comprehensive validation and stress testing

## ð ï¸ Development Workflow

1. **Code Changes**: Edit files in `src/` or root directory
2. **Testing**: Run tests from `testing/` directory
3. **Documentation**: Update docs in `docs/` directory
4. **Strategies**: Modify trading logic in `strategies/` directory
5. **Configuration**: Adjust settings in `config/` directory

## ð Production Ready

[ok] **Clean Architecture**: Organized directory structure  
[ok] **Comprehensive Testing**: Full test coverage  
[ok] **Professional Documentation**: Complete user guides  
[ok] **VS Code Integration**: Optimized development environment  
[ok] **Dependency Management**: Clean requirements.txt  
[ok] **Error Handling**: Robust exception management  

---
*Last Updated: September 2025 - Project successfully organized and cleaned* ð