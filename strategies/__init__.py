"""
MT5 Live Trading Bot - Sunrise Strategies
==========================================

This module contains independent copies of the Sunrise trading strategies
for use with the MT5 live trading system.

These strategies are completely independent from the original quant_bot_project
development environment and can be used for live trading without external dependencies.

Available Strategies:
- kips_strategy_eurusd: EUR/USD trading strategy
- kips_strategy_gbpusd: GBP/USD trading strategy  
- kips_strategy_xauusd: Gold (XAU/USD) trading strategy
- kips_strategy_audusd: AUD/USD trading strategy
- kips_strategy_xagusd: Silver (XAG/USD) trading strategy
- kips_strategy_usdchf: USD/CHF trading strategy
"""

# Import all strategies for easier access
try:
    from .kips_strategy_eurusd import KipsStrategy as KipsStrategyEURUSD
except ImportError:
    KipsStrategyEURUSD = None

try:
    from .kips_strategy_gbpusd import KipsStrategy as KipsStrategyGBPUSD
except ImportError:
    KipsStrategyGBPUSD = None

try:
    from .kips_strategy_xauusd import KipsStrategy as KipsStrategyXAUUSD
except ImportError:
    KipsStrategyXAUUSD = None

try:
    from .kips_strategy_audusd import KipsStrategy as KipsStrategyAUDUSD
except ImportError:
    KipsStrategyAUDUSD = None

try:
    from .kips_strategy_xagusd import KipsStrategy as KipsStrategyXAGUSD
except ImportError:
    KipsStrategyXAGUSD = None

try:
    from .kips_strategy_usdchf import KipsStrategy as KipsStrategyUSDCHF
except ImportError:
    KipsStrategyUSDCHF = None

# Export all available strategies
__all__ = [
    'KipsStrategyEURUSD',
    'KipsStrategyGBPUSD', 
    'KipsStrategyXAUUSD',
    'KipsStrategyAUDUSD',
    'KipsStrategyXAGUSD',
    'KipsStrategyUSDCHF'
]

# Strategy mapping for easy access
STRATEGY_CLASSES = {
    'EURUSD': KipsStrategyEURUSD,
    'GBPUSD': KipsStrategyGBPUSD,
    'XAUUSD': KipsStrategyXAUUSD,
    'AUDUSD': KipsStrategyAUDUSD,
    'XAGUSD': KipsStrategyXAGUSD,
    'USDCHF': KipsStrategyUSDCHF
}