# Kips MT5 Live Trading Bot

> Institutional-grade automated trading system implementing Ray Dalio's All-Weather Portfolio allocation

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MetaTrader 5](https://img.shields.io/badge/MetaTrader-5-green.svg)](https://www.metatrader5.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Charts: TradingView](https://img.shields.io/badge/Charts-TradingView%20Engine-blueviolet.svg)](https://pypi.org/project/lightweight-charts/)

![MT5 Advanced Monitor GUI](docs/Advanced%20MT5%20Monitor.png)

---

## What This Bot Does

- **8-Asset Portfolio** - Trades EURUSD, GBPUSD, XAUUSD, AUDUSD, XAGUSD, USDCHF, EURJPY, USDJPY on M5
- **Ray Dalio Allocation** - Economic scenario-based position sizing across all assets
- **6-Layer Entry Filters** - Validates ATR, Angle, Price, Candle Direction, EMA Ordering, and Time before every trade
- **Real-Time Interactive Charts** - TradingView-engine (lightweight-charts) with live candlesticks, 5 EMA overlays, ATR SL/TP lines, and armed-direction markers; falls back to matplotlib if lightweight-charts is not installed
- **4-Phase State Machine** - SCANNING > ARMED > WINDOW_OPEN > ENTRY with pullback confirmation
- **MT5 Broker Integration** - Dynamic position sizing using broker-specific tick values (not hardcoded)
- **Dynamic Drawdown Cap** - Automatically tightens as the account grows, viable from $100 upwards
- **Two Trading Modes** - NORMAL (conservative) and AGGRESSIVE with different risk and DD limits

---

## Quick Start

### 1. Installation

```powershell
# Clone repository
git clone https://github.com/kipsviii-dev/MT5Bot.git
cd mt5_live_trading_bot

# Automated setup (Windows PowerShell - Recommended)
.\setup.ps1

# OR Manual setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt

# Verify chart engine (lightweight-charts is preferred)
# If lightweight-charts installed → TradingView engine active
# If only matplotlib installed   → fallback mode active
python -c "from lightweight_charts import Chart; print('TradingView engine: OK')"
```

### 2. Configuration

```bash
# Copy MT5 credentials template
copy config\mt5_credentials_template.json config\mt5_credentials.json
# Edit with your MT5 account details (account number, password, server)
```

### 3. Launch

```bash
# Start the trading bot
python advanced_mt5_monitor_gui.py

# OR run executable (Windows)
dist\MT5_Trading_Bot.exe
```

---

## System Architecture

### Ray Dalio All-Weather Portfolio Allocation (v2.1)

Economic scenario-based position sizing with two trading modes and a dynamic drawdown cap:

| Asset | Allocation | Economic Role |
|-------|-----------|---------------|
| XAUUSD | 15% | Inflation hedge (gold) |
| USDCHF | 15% | Deflation hedge (safe haven) |
| GBPUSD | 12% | Balanced forex |
| EURUSD | 12% | Balanced forex |
| XAGUSD | 12% | Commodity (silver) |
| AUDUSD | 10% | Commodity currency |
| EURJPY | 12% | JPY cross (carry trade) |
| USDJPY | 12% | JPY core pair |

### Trading Modes

Two modes are available and can be switched from the GUI at any time:
|---|---|---|
| Per-trade risk | 1% of allocated | 3% of allocated |
| DD cap at $100 | 40% | 60% |
| DD cap at $2,000+ | 10% | 20% |
| Layers per symbol | 1 | 3 |

The dynamic DD cap shrinks automatically as the balance grows - protecting profits without manual changes.

> Full documentation: [DALIO_ALLOCATION_SYSTEM.md](docs/DALIO_ALLOCATION_SYSTEM.md) | [DALIO_QUICK_REFERENCE.md](docs/DALIO_QUICK_REFERENCE.md)

---

### 6-Layer Entry Filter Cascade

Every signal must pass **ALL** filters to prevent false entries, applied in two stages:

**Stage 1 - Crossover Validation (Scanning)**

```
EMA Crossover Detected
      |
  [1] ATR Filter      - Volatility in valid range?
  [2] Angle Filter    - EMA slope meets requirements?
  [3] Price Filter    - Price aligned with trend?
  [4] Candle Filter   - Previous candle confirms momentum?
  [5] EMA Ordering    - Multi-EMA sequence correct?
      |
ALL PASSED --> ARMED State --> Pullback --> Window
ANY FAILED --> REJECTED (stay in SCANNING)
```

**Stage 2 - Entry Validation (Window Breakout)**

```
Window Breakout Detected
      |
  [6] Time Filter     - Within trading hours?
      |
PASSED --> ENTRY
FAILED --> SKIP (return to SCANNING)
```

Result: Reduces entries from ~240/month to ~2-3/month per asset (matches backtesting).

---

### 4-Phase State Machine

```
+------------------------------------------------------+
|  SCANNING - Monitoring for valid crossovers          |
+------------------------------------------------------+
                     | All filters pass
+------------------------------------------------------+
|  ARMED - Waiting for pullback confirmation (1-3 bars)|
|  Global invalidation: counter-crossover resets state |
+------------------------------------------------------+
                     | Pullback complete
+------------------------------------------------------+
|  WINDOW_OPEN - 2-sided breakout window active        |
|  Success boundary --> execute trade                  |
|  Failure boundary --> reset to SCANNING              |
+------------------------------------------------------+
                     | Breakout detected
+------------------------------------------------------+
|  ENTRY - Trade executed with ATR-based SL/TP         |
+------------------------------------------------------+
```

---

## Latest Updates (March 2026)

### TradingView-Engine Charts — lightweight-charts Integration (March 2026)

The charting panel has been completely upgraded from matplotlib to the **TradingView Lightweight Charts engine** (`lightweight-charts` Python package). MT5 remains the sole broker, data source, and execution engine — only the visualisation layer changed.

**What's new:**

| Feature | Before (matplotlib) | After (lightweight-charts) |
|---|---|---|
| Chart type | Static re-render on every tick | Live push — only changed candles update |
| Interactivity | Fixed zoom via toolbar | Scroll, pinch-zoom, crosshair out of the box |
| Overlays | 5 EMAs plotted as lines | 5 EMA line series (`EMA Confirm / Fast / Medium / Slow / Filter`) |
| SL / TP levels | Static `axhline` | Interactive price lines (shown/hidden per phase) |
| Trade markers | None | ▲ / ▼ arrow markers on the last bar when ARMED |
| Watermark | Chart title string | Dynamic symbol + phase + ATR watermark |
| Engine | `matplotlib` / `FigureCanvasTkAgg` | `lightweight_charts.Chart` (floating window) |
| Fallback | N/A | Full matplotlib path kept — activates automatically if `lightweight-charts` is not installed |

**How the engine selection works:**

```python
# At startup (top of advanced_mt5_monitor_gui.py)
CHART_ENGINE = "lightweight"   # if lightweight-charts is installed  ← preferred
CHART_ENGINE = "matplotlib"    # fallback if only matplotlib present
CHART_ENGINE = "none"          # if neither is installed
```

`refresh_chart()` dispatches to `_refresh_lightweight_chart()` or `_refresh_matplotlib_chart()` transparently. Every callout that previously checked `if MATPLOTLIB_AVAILABLE` now checks `if CHART_ENGINE != "none"` so both engines are handled by a single gate.

**Auto-refresh triggers (both fast and full monitoring paths):**

- Monitoring loop — fast path (price-only update)
- Monitoring loop — full path (indicator recalculation)
- Strategy phase selection in the phase tree
- Symbol selector combo-box change
- Manual "Refresh Chart" button

**Install the primary engine:**

```powershell
pip install lightweight-charts
```

If `lightweight-charts` is already present, no action needed — it is automatically preferred over matplotlib.

---

### Ray Dalio Allocation v2.1 - Dynamic Drawdown Cap + Trading Modes

The risk management system has been upgraded with two selectable trading modes and a dynamic drawdown cap that scales automatically with account balance.

**Two Trading Modes** (selectable from the GUI):

| | NORMAL | AGGRESSIVE |
|---|---|---|
| Per-trade risk | 1% of allocated capital | 3% of allocated capital |
| Kill zones active | London Open + NY AM | All 5 ICT kill zones |
| Max layers per symbol | 1 | 3 |
| DD cap at $100 | 40% | 60% |
| DD cap at $500 | 26% | 44% |
| DD cap at $1,000 | 18% | 32% |
| DD cap at $2,000+ | 10% | 20% |

**Dynamic Drawdown Cap** - Instead of a fixed DD limit, the cap tightens linearly as the balance grows. A $100 account gets a generous 40% cap to stay alive through volatility. A $2,000+ account is protected with a strict 10% cap to preserve profits.

**Small-Balance Guard** - On accounts below $500, the minimum risk per trade is clamped to $0.50 to prevent zero-lot situations that would block all trading.

**AGGRESSIVE mode warning** - Switching to AGGRESSIVE triggers a confirmation dialog explaining the higher risk profile before it activates.

**Mode-aware LayerManager** - `src/layer_manager.py` enforces all layer limits, DD triggers, and breakeven logic dynamically based on the selected mode.

---

## Previous Updates

### JPY Pairs and 8-Asset Portfolio (December 2025)

Expanded portfolio to 8 assets with JPY pair support:
- EURJPY - 12% allocation, JPY cross exposure
- USDJPY - 12% allocation, JPY carry trade
- JPY pairs use 3 decimal places, pip value = 0.01, scale factor = 100

### UTC Timezone and DST Fix (November 2025)

- Added UTC offset selector (UTC+1 / UTC+2) for Daylight Savings Time handling
- All strategy time filters now convert broker time to UTC automatically

### Position Sizing Fix (November 2025)

Now uses MT5 broker-specific tick values instead of hardcoded pip values:

```python
# Before (broken)
# GBPUSD: Risk $22.70 instead of $80.13 (3.53x too small)
# XAGUSD: Risk $0.46 instead of $75.12 (163x too small)

# After (fixed)
tick_value = mt5.symbol_info(symbol).trade_tick_value
lot_size = risk_amount / (sl_distance * value_per_point)
```

### ATR Filter Implementation (October 2025)

Fixed ATR filter not validating entries due to missing dataframe integration.
Reduced entries from ~240/month to ~2-3/month per asset (matches backtesting).

---

## Project Structure

```
mt5_live_trading_bot/
|-- advanced_mt5_monitor_gui.py       # Main bot (3,500+ lines)
|-- requirements.txt                  # Python dependencies
|-- setup.ps1                         # Automated setup
|-- build_exe.bat                     # Build Windows executable
|
|-- strategies/                       # Asset-specific strategy files (READ-ONLY)
|   |-- kips_strategy_eurusd.py
|   |-- kips_strategy_gbpusd.py
|   |-- kips_strategy_xauusd.py
|   |-- kips_strategy_audusd.py
|   |-- kips_strategy_xagusd.py
|   |-- kips_strategy_usdchf.py
|   |-- kips_strategy_eurjpy.py
|   |-- kips_strategy_usdjpy.py
|
|-- src/                              # Core modules
|   |-- layer_manager.py              # Mode-aware position layering
|   |-- htf_trend_filter.py           # 4H trend filter
|   |-- session_manager.py            # Session/kill zone logic
|   |-- mt5_live_trading_connector.py
|   |-- sunrise_signal_adapter.py
|
|-- testing/                          # Test suite
|   |-- test_setup.py
|   |-- check_broker_specs.py
|   |-- test_position_sizing.py
|   |-- verify_all_symbols.py
|   |-- test_jpy_entries.py
|
|-- docs/                             # Documentation
|   |-- README.md                     # Documentation index
|   |-- DALIO_ALLOCATION_SYSTEM.md
|   |-- DALIO_QUICK_REFERENCE.md
|   |-- START_TESTING_HERE.md
|   |-- DEPLOYMENT_GUIDE.md
```

> Strategy files are READ-ONLY to preserve backtesting integrity.
> See [STRATEGY_FILES_POLICY.md](docs/STRATEGY_FILES_POLICY.md)

---

## Risk Management

### Safety Features

- **Ray Dalio Allocation v2.1** - Two modes (NORMAL/AGGRESSIVE), dynamic DD cap from $100 to $2,000+
- **Portfolio Drawdown Guard** - Blocks all new entries once the DD cap is reached
- **Simultaneous Risk Guard** - Caps total open exposure across all positions
- **Small-Balance Guard** - Keeps the bot viable on accounts as small as $100
- **6-Layer Filters** - Validates every signal before entry
- **ATR-Based SL/TP** - Dynamic stop loss and take profit per trade
- **MT5 Broker Integration** - Uses actual broker tick values (not hardcoded)
- **Global Invalidation** - Counter-trend crossovers reset armed states
- **Duplicate Prevention** - Checks existing positions before placing orders
- **Time Filters** - Trading hour restrictions per asset

### Warnings

- Never risk more than you can afford to lose
- Understand the system completely before going live
- Start with minimum position sizes on a demo account
- Keep detailed logs of all trading activity
- Strategy files are READ-ONLY - do not modify them

---

## Testing

```bash
cd testing

# 1. Installation check
python test_setup.py

# 2. Broker specifications
python check_broker_specs.py

# 3. Position sizing validation
python test_position_sizing.py

# 4. Symbol configuration check
python verify_all_symbols.py

# 5. Order execution test (places real orders - demo only!)
python test_mt5_order.py
```

---

## Configuration

### MT5 Credentials (`config/mt5_credentials.json`)

```json
{
  "account": 12345678,
  "password": "YourPassword",
  "server": "YourBroker-Demo"
}
```

### Strategy Parameters

Each file in `strategies/` contains:
- EMA periods (Fast, Medium, Slow, Filter)
- ATR multipliers (SL: 4.5x, TP: 6.5x default)
- Pullback requirements (1-3 candles)
- Window duration (1-20 bars)
- Trading hours (UTC)
- `TRADING_MODE` - set to `'NORMAL'` or `'AGGRESSIVE'`

---

## GUI Features

- **Asset Dashboard** - Price, state, pullback count, window status per symbol
- **Live Interactive Charts** - TradingView-engine candlesticks with 5 EMA overlays, ATR SL/TP price lines, and armed-direction arrow markers (falls back to matplotlib if lightweight-charts is absent)
- **Strategy States** - Color-coded phase indicators (SCANNING, ARMED, WINDOW_OPEN)
- **Mode Selector** - NORMAL / AGGRESSIVE radio buttons with live DD cap display
- **Configuration Viewer** - Complete strategy parameters and filter details
- **Terminal Logging** - Real-time event log with timestamps

---

## Troubleshooting

**MT5 Connection Failed**
- Ensure MT5 terminal is running and logged in
- Verify credentials in `config/mt5_credentials.json`
- Check that the MetaTrader5 Python package is installed
- Restart MT5 terminal

**No Signals Detected**
- Confirm the market is open for selected assets
- Check if price data is streaming (see `logs/`)
- Review filter thresholds (may be too strict)
- Verify strategy files loaded (check terminal output)

**Position Sizing Issues**
- Run `testing/check_broker_specs.py`
- Verify MT5 account balance is fetched correctly
- Check logs for the broker specifications section
- Confirm tick_value matches the broker contract specs

---

## Documentation

| Document | Description |
|----------|-------------|
| [DALIO_ALLOCATION_SYSTEM.md](docs/DALIO_ALLOCATION_SYSTEM.md) | Full allocation system docs (v2.1) |
| [DALIO_QUICK_REFERENCE.md](docs/DALIO_QUICK_REFERENCE.md) | Risk tables and scaling chart |
| [START_TESTING_HERE.md](docs/START_TESTING_HERE.md) | Testing guide |
| [DEPLOYMENT_GUIDE.md](docs/DEPLOYMENT_GUIDE.md) | Full deployment steps |
| [STRATEGY_FILES_POLICY.md](docs/STRATEGY_FILES_POLICY.md) | READ-ONLY strategy policy |
| [docs/README.md](docs/README.md) | Full documentation index |

---

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/MyFeature`)
3. Read [STRATEGY_FILES_POLICY.md](docs/STRATEGY_FILES_POLICY.md) - strategy files are READ-ONLY
4. Test on a demo account thoroughly
5. Document changes and include test results
6. Submit a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Disclaimer

**This software is for educational purposes only.** Trading forex and commodities involves substantial risk of loss. Past performance is not indicative of future results. No representation is made that any account will achieve profits similar to those discussed. Use at your own risk. The developers assume no responsibility for trading results.

---

## Acknowledgments

- MetaTrader 5 Python API
- Ray Dalio's All-Weather Portfolio principles
- [lightweight-charts](https://pypi.org/project/lightweight-charts/) — TradingView-engine charting (primary)
- matplotlib / mplfinance — fallback charting
- Backtrader for strategy development
