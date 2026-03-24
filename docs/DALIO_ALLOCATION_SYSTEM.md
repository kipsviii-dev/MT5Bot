# Ray Dalio All-Weather Portfolio Allocation System

> **Version:** 2.1  -  Dynamic Drawdown Scaling + Trading Modes  
> **Last Updated:** March 25, 2026  
> **Status:** [ok] IMPLEMENTED

---

## Overview

This document explains the Ray Dalio All-Weather Portfolio implementation in the MT5 Live Trading Bot.

The system provides **economic scenario-based position sizing** across 8 assets, now enhanced with:

- **Two trading modes**  -  NORMAL (capital preservation) and AGGRESSIVE (max growth)
- **Dynamic drawdown cap**  -  the DD limit automatically tightens as your account grows
- **Small-balance guard**  -  keeps the bot viable on accounts as small as $100

---

## ð Asset Allocation

| **Asset** | **Allocation** | **Economic Role** |
|-----------|---------------|-------------------|
| USDCHF | 15% | Deflation hedge (safe haven) |
| XAUUSD | 15% | Inflation hedge (gold) |
| GBPUSD | 12% | Balanced forex |
| EURUSD | 12% | Balanced forex |
| XAGUSD | 12% | Commodity / industrial metal |
| AUDUSD | 10% | Commodity currency |
| EURJPY | 12% | JPY cross (carry trade) |
| USDJPY | 12% | JPY core pair (BOJ sensitivity) |

**Total: 100%**

---

## ð­ Trading Modes

### ð¡ NORMAL  -  Capital Preservation

| Parameter | Value |
|-----------|-------|
| Per-trade risk | 1% of allocated capital |
| DD cap at $100 | **40%** of balance |
| DD cap at $2,000+ | **10%** of balance |
| Max simultaneous risk | 6% of balance |
| Max layers per symbol | 1 |

### [!] AGGRESSIVE  -  Maximum Growth

| Parameter | Value |
|-----------|-------|
| Per-trade risk | 3% of allocated capital |
| DD cap at $100 | **60%** of balance |
| DD cap at $2,000+ | **20%** of balance |
| Max simultaneous risk | 50% of balance |
| Max layers per symbol | 3 |

---

## ð Dynamic Drawdown Cap

The DD cap is **not fixed**. It scales down linearly as the account grows:

```
balance â¤ $100   -> use HIGH cap   (40% NORMAL / 60% AGGRESSIVE)
balance â¥ $2,000 -> use FLOOR cap  (10% NORMAL / 20% AGGRESSIVE)
between          -> linear interpolation
```

### Scaling Table

| Balance | ð¡ NORMAL cap | [!] AGGRESSIVE cap |
|---------|--------------|------------------|
| **$100** | **40%** | **60%** |
| $250 | 34% | 53% |
| $500 | 27% | 47% |
| $750 | 21% | 40% |
| $1,000 | 18% | 35% |
| $1,500 | 13% | 27% |
| **$2,000+** | **10%** | **20%** |

**Why this matters:** On a $100 account you need room to grow. At $2,000+ you have real capital worth protecting  -  the system tightens automatically with zero manual intervention.

---

## ð° Position Sizing Formula

```
risk_amount = balance Ã allocation_pct Ã risk_pct
```

### Example  -  $100 account, NORMAL mode, XAUUSD

```
allocated_capital = $100 Ã 15% = $15.00
risk_amount       = $15.00 Ã 1% = $0.15
-> Small-balance guard scales to $0.50 minimum
DD cap            = 40% (dynamic, at $100 balance)
```

### Example  -  $100 account, AGGRESSIVE mode, XAUUSD

```
allocated_capital = $100 Ã 15% = $15.00
risk_amount       = $15.00 Ã 3% = $0.45
-> Small-balance guard scales to $0.50 minimum
DD cap            = 60% (dynamic, at $100 balance)
```

### Example  -  $1,000 account, NORMAL mode, XAUUSD

```
allocated_capital = $1,000 Ã 15% = $150.00
risk_amount       = $150.00 Ã 1% = $1.50
DD cap            = 18% -> blocks entries if equity drops below $820
```

---

## ð¡ Three Safety Guards (executed before every trade)

```
Trade Signal Detected
        â
â  Portfolio Drawdown Guard
   -> Is current DD% â¥ dynamic cap? BLOCK ALL ENTRIES
        â
â¡ Dalio Risk Calculation
   -> Compute risk_amount (mode + balance + small-balance guard)
        â
â¢ Simultaneous Risk Guard
   -> Would total open risk exceed mode's exposure cap? BLOCK
        â
[ok] Execute Trade
```

---

## âï¸ Configuration

### Switching Trading Mode

In the GUI: use the **Trading Mode** radio buttons in the Monitoring Controls panel.

To set a code default, edit `advanced_mt5_monitor_gui.py`:

```python
ACTIVE_TRADING_MODE = TRADING_MODE_NORMAL      # safe
ACTIVE_TRADING_MODE = TRADING_MODE_AGGRESSIVE  # max growth
```

### Adjusting the DD Scaling Range

```python
# Balance thresholds (in advanced_mt5_monitor_gui.py)
DD_SCALE_START_BALANCE = 100.0    # below this -> use HIGH cap
DD_SCALE_FLOOR_BALANCE = 2000.0   # above this -> use FLOOR cap

# NORMAL cap range
DD_CAP_HIGH_NORMAL   = 0.40   # 40% at small balance
DD_CAP_FLOOR_NORMAL  = 0.10   # 10% at large balance

# AGGRESSIVE cap range
DD_CAP_HIGH_AGGRESSIVE  = 0.60
DD_CAP_FLOOR_AGGRESSIVE = 0.20
```

### Per-Asset Risk Override

```python
# In strategies/kips_strategy_xauusd.py
class Config:
    RISK_PER_TRADE = 0.015  # override to 1.5% for this asset
```

### Asset Allocation Weights

```python
ASSET_ALLOCATIONS = {
    'USDCHF': 0.15,
    'XAUUSD': 0.15,
    # ...
}
```

Ensure allocations sum to 1.00.

---

## ð Strategy Files Policy

This system modifies **only** `advanced_mt5_monitor_gui.py` and `src/layer_manager.py`.

**Strategy files in `strategies/` remain READ-ONLY** per `STRATEGY_FILES_POLICY.md`.

---

## ð Deployment Checklist

- [x] Dynamic DD cap (`_compute_dynamic_dd_cap`)
- [x] Two trading modes (NORMAL / AGGRESSIVE)
- [x] Small-balance guard (min $0.50 risk)
- [x] Portfolio drawdown guard (pass `balance` to `_get_mode_params`)
- [x] Simultaneous risk guard
- [x] GUI trading mode selector with warning dialog
- [x] Mode-aware `LayerManager` (`src/layer_manager.py`)
- [ ] Test on demo account at $100 balance
- [ ] Verify DD cap shrinks correctly as balance grows
- [ ] Monitor first 5 trades for accuracy

---

## ð References

- Ray Dalio's All-Weather Portfolio  -  Bridgewater Associates
- Modern Portfolio Theory  -  Harry Markowitz
- `src/layer_manager.py`  -  LayerManager (NORMAL/AGGRESSIVE mode-aware)
- `advanced_mt5_monitor_gui.py` lines 80 - 240  -  full implementation

---

**Implementation Date:** March 25, 2026  
**Version:** 2.1  
**Previous Version:** 1.0 (static 1% risk, no modes, no dynamic DD)
