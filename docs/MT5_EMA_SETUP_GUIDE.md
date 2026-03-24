# HOW TO DISPLAY BACKTRADER EMAs IN MT5

## ð¯ **OBJECTIVE**
Display the SAME EMAs in MT5 that match your backtrader strategy calculations.

---

## ð **BACKTRADER EMA CALCULATION**

Your strategy uses: `bt.ind.EMA(d.close, period=X)`

Backtrader's EMA formula:
```
EMA = (Close Ã Î±) + (Previous_EMA Ã (1 - Î±))
Where: Î± = 2 / (period + 1)
```

This is the **standard EMA** (also called **Exponential Moving Average** or **EMA Wilder**).

---

## ð§ **MT5 INDICATOR SETUP**

### **Step 1: Add EMA Indicator in MT5**

1. **Open MT5** -> Click on your EURUSD M5 chart
2. **Insert -> Indicators -> Trend -> Moving Average**
3. **Configure EACH EMA** with these EXACT settings:

---

### **ð EMA CONFIRM (Period: 1)**

| Parameter | Value |
|-----------|-------|
| **Period** | `1` |
| **MA Method** | `Exponential` |
| **Apply to** | `Close` |
| **Shift** | `0` |
| **Color** | Cyan/Turquoise |
| **Style** | Solid line, Width 1 |

---

### **ð EMA FAST (Period: 18)**

| Parameter | Value |
|-----------|-------|
| **Period** | `18` |
| **MA Method** | `Exponential` |
| **Apply to** | `Close` |
| **Shift** | `0` |
| **Color** | Orange |
| **Style** | Solid line, Width 2 |

---

### **ð EMA MEDIUM (Period: 18)**

| Parameter | Value |
|-----------|-------|
| **Period** | `18` |
| **MA Method** | `Exponential` |
| **Apply to** | `Close` |
| **Shift** | `0` |
| **Color** | Green |
| **Style** | Solid line, Width 2 |

[warn]ï¸ **NOTE**: Fast and Medium both use period 18 in EURUSD strategy!

---

### **ð EMA SLOW (Period: 24)**

| Parameter | Value |
|-----------|-------|
| **Period** | `24` |
| **MA Method** | `Exponential` |
| **Apply to** | `Close` |
| **Shift** | `0` |
| **Color** | Dark Green |
| **Style** | Solid line, Width 2 |

---

### **ð EMA FILTER (Period: 70)**

| Parameter | Value |
|-----------|-------|
| **Period** | `70` |
| **MA Method** | `Exponential` |
| **Apply to** | `Close` |
| **Shift** | `0` |
| **Color** | Purple |
| **Style** | Solid line, Width 2 |

---

## [ok] **VERIFICATION**

After adding all EMAs, your MT5 chart should show:
- **Cyan line** (EMA 1) - follows price exactly
- **Orange line** (EMA 18 Fast)
- **Green line** (EMA 18 Medium) - same as orange
- **Dark Green line** (EMA 24 Slow) - slightly below/above others
- **Purple line** (EMA 70 Filter) - smoothest, slowest

These should **EXACTLY match** the EMAs shown in your bot's GUI!

---

## ð¬ **WHY MT5 STANDARD EMA MATCHES BACKTRADER**

Both use the same formula:

**Backtrader**:
```python
bt.ind.EMA(period=18)
# Uses: EMA = (Close Ã Î±) + (Previous_EMA Ã (1 - Î±))
# Where: Î± = 2 / (18 + 1) = 0.1053
```

**MT5 Exponential MA**:
```
Method: Exponential
Period: 18
# Uses: EMA = (Close Ã 2/(18+1)) + (Previous_EMA Ã (1 - 2/(18+1)))
# Same formula!
```

---

## [warn]ï¸ **IMPORTANT NOTES**

### **DO NOT USE These MT5 Indicators:**
- â **Triple Exponential Moving Average (TEMA)** - Different formula
- â **Double Exponential Moving Average (DEMA)** - Different formula
- â **Moving Average (SMA)** - Simple average, not exponential
- â **Smoothed Moving Average (SMMA)** - Different smoothing method

### **ONLY USE:**
- [ok] **Moving Average -> Method: Exponential** - This matches backtrader!

---

## ð¸ **EXAMPLE MT5 SETUP**

After setup, your MT5 "Indicators List" should show:
```
ð Main Chart
   |-- Moving Average(1) - EMA Confirm - Cyan
   |-- Moving Average(18) - EMA Fast - Orange
   |-- Moving Average(18) - EMA Medium - Green
   |-- Moving Average(24) - EMA Slow - Dark Green
   `-- Moving Average(70) - EMA Filter - Purple
```

---

## ð¨ **RECOMMENDED COLOR SCHEME**

To match your bot's GUI colors:

| EMA | Period | Color | Hex Code |
|-----|--------|-------|----------|
| Confirm | 1 | Cyan | #00FFFF |
| Fast | 18 | Orange | #FF8C00 |
| Medium | 18 | Green | #00FF00 |
| Slow | 24 | Dark Green | #008000 |
| Filter | 70 | Purple | #800080 |

---

## ð **APPLY TO ALL SYMBOLS**

Repeat this setup for:
- [ok] EURUSD M5
- [ok] GBPUSD M5
- [ok] XAUUSD M5
- [ok] AUDUSD M5
- [ok] XAGUSD M5
- [ok] USDCHF M5

**TIP**: After setting up one chart, right-click -> **Template -> Save Template** -> Name it "Sunrise_Strategy"
Then apply to other charts: Right-click -> **Template -> Load Template -> Sunrise_Strategy**

---

## ð§ª **TESTING ALIGNMENT**

To verify EMAs match:

1. **Open MT5** with EMAs configured
2. **Open Bot GUI** showing same symbol
3. **Compare EMA values** at current price
4. **Check crossover points** - should occur at same candles

If values don't match exactly (±0.0001), check:
- [ok] Period is correct
- [ok] Method is "Exponential" (not Simple, Smoothed, etc.)
- [ok] Applied to "Close" price
- [ok] Shift is 0

---

## ð **QUICK REFERENCE CARD**

**EURUSD Strategy EMAs:**
```
EMA Confirm:  Period 1   (Cyan)
EMA Fast:     Period 18  (Orange)
EMA Medium:   Period 18  (Green)
EMA Slow:     Period 24  (Dark Green)
EMA Filter:   Period 70  (Purple)
```

**All using:**
- Method: **Exponential**
- Apply to: **Close**
- Shift: **0**

---

## [ok] **FINAL CHECK**

After setup, verify crossover detection:

**Example**: When bot shows:
```
ð¯ EURUSD: LONG CROSSOVER - State: SCANNING -> ARMED_LONG
```

MT5 chart should show:
- Cyan line (Confirm EMA) crossing ABOVE one of:
  - Orange line (Fast EMA), or
  - Green line (Medium EMA), or
  - Dark Green line (Slow EMA)

If you see this alignment -> **Perfect! EMAs match!** [ok]

---

**Created**: October 14, 2025  
**For**: MT5 Live Trading Bot - Sunrise Strategy  
**Compatibility**: Backtrader EMA = MT5 Exponential MA
