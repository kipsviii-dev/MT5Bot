# IMPORTANT: Strategy Files Policy

**Date:** October 22, 2025  
**Status:** [ok] CORRECTED

---

## Critical Rule Established

### â NEVER MODIFY STRATEGY FILES

The files in `strategies/` folder are the **SOURCE OF TRUTH** for backtesting:

```
strategies/
|-- kips_strategy_audusd.py    â READ ONLY
|-- kips_strategy_eurusd.py    â READ ONLY  
|-- kips_strategy_gbpusd.py    â READ ONLY
|-- kips_strategy_usdchf.py    â READ ONLY
|-- kips_strategy_xagusd.py    â READ ONLY
`-- kips_strategy_xauusd.py    â READ ONLY
```

---

## Why This Is Critical

### 1. Backtrader Dependency
- All backtesting is based on these original files
- Any modification breaks historical validation
- No way to verify if changes match backtest results

### 2. Control & Verification
- User needs unmodified originals for comparison
- Changes make it impossible to track what was tested
- Originals are the benchmark for live performance

### 3. Separation of Concerns
- **Strategy files:** Pure backtrader strategy logic
- **GUI monitor:** Live MT5 implementation (can be modified)

---

## What Was Corrected

### Changes Made (and Reverted)
- â Added type: ignore comments
- â Modified pullback logic  
- â Changed global invalidation
- â Added None checks

**All reverted using:** `git checkout -- strategies/`

### Current Status
[ok] All 6 strategy files restored to original state  
[ok] No changes in strategies/ folder  
[ok] Git working tree clean for strategies/

---

## Correct Approach Going Forward

### [ok] DO: Modify GUI Monitor
All fixes should go in:
- `advanced_mt5_monitor_gui.py` [ok] ALLOWED

This file adapts the strategy logic for live MT5 trading and can be modified freely.

### â DON'T: Modify Strategy Files
These files are READ-ONLY:
- `strategies/kips_strategy_*.py` â FORBIDDEN

If backtrader strategy needs changes, user must do it manually after verification.

---

## Documentation Updated

Created:
- [ok] This file (`STRATEGY_FILES_POLICY.md`)
- [ok] Warning in all relevant documentation

Removed:
- â `STRATEGY_FILES_CHANGES_ANALYSIS.md` (no longer relevant)
- â All references to modifying strategy files

---

## Final Commit Contents

### What's Being Committed:

1. **advanced_mt5_monitor_gui.py**
   - All 7 pullback bugs fixed
   - EMA stability improvements
   - Enhanced logging
   - Chart navigation

2. **docs/** (cleaned)
   - 18 essential documentation files
   - 29 files moved to archive/
   - New README.md

3. **.gitignore**
   - Added docs/archive/ exclusion

### What's NOT Being Committed:

4. **strategies/** [ok] UNCHANGED
   - All files reverted to original
   - No modifications
   - Backtrader integrity preserved

---

## Lesson Learned

**AI Assistant should:**
- [ok] Read strategy files for understanding
- [ok] Implement logic in GUI monitor
- [ok] Document differences between backtrader and live implementation
- â NEVER modify strategy files directly

**User controls:**
- [ok] Strategy file modifications (manual only)
- [ok] Backtrader testing and validation
- [ok] Approval of any strategy logic changes

---

## Updated Commit Message

```bash
fix: Critical pullback detection + EMA bugs in GUI monitor

ROOT CAUSE (Bug 6): Double candle removal in crossover detection
- Fixed iloc[-2] -> iloc[-1] for current closed candle (line 829)
- Fixed df[:-1] -> df for EMA calculation (line 848)

ALL 7 BUGS FIXED:
- Bug 1-5: Previous pullback fixes
- Bug 6: Crossover detection on stale data
- Bug 7: Signal trigger candle wrong index

EMA IMPROVEMENTS:
- 500 bars historical data (was 100)
- adjust=False for MT5/backtrader alignment
- Dynamic symbol precision

ENHANCED LOGGING:
- Export-ready terminal logs
- OHLC values for every candle checked
- Emoji markers for analysis

DOCS CLEANUP:
- 62% reduction (29 files archived)
- 18 essential files kept
- Added docs/archive/ to .gitignore

CHART NAVIGATION:
- Plotly-style interactive controls

IMPORTANT: Strategy files (strategies/*.py) unchanged - 
all fixes in GUI monitor only (advanced_mt5_monitor_gui.py)

Files: advanced_mt5_monitor_gui.py, docs/, .gitignore
Strategy files: UNCHANGED (backtrader originals preserved)
```

---

**Policy Established:** October 22, 2025  
**Verified By:** User  
**Status:** [ok] ENFORCED
