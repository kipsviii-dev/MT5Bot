# Dalio Allocation  -  Quick Reference (v2.1)

> Last updated: March 25, 2026

---

## Trading Modes at a Glance

| | ð¡ NORMAL | [!] AGGRESSIVE |
|---|---|---|
| Per-trade risk | 1% of allocated | 3% of allocated |
| DD cap @ $100 | **40%** | **60%** |
| DD cap @ $2,000+ | **10%** | **20%** |
| Max simultaneous risk | 6% of balance | 50% of balance |
| Layers per symbol | 1 | 3 |
| Floating DD de-risk | 3% of equity | 15% of equity |

---

## Dynamic DD Cap  -  Full Scaling Table

| Balance | ð¡ NORMAL cap | [!] AGGRESSIVE cap |
|---------|--------------|------------------|
| $100 | 40% | 60% |
| $250 | 34% | 53% |
| $500 | 27% | 47% |
| $750 | 21% | 40% |
| $1,000 | 18% | 35% |
| $1,500 | 13% | 27% |
| $2,000+ | 10% | 20% |

Cap shrinks automatically as balance grows  -  no manual changes needed.

---

## Asset Allocations

| Symbol | Allocation | Role |
|--------|-----------|------|
| USDCHF | 15% | Deflation hedge |
| XAUUSD | 15% | Inflation hedge |
| GBPUSD | 12% | Balanced forex |
| EURUSD | 12% | Balanced forex |
| XAGUSD | 12% | Commodity (silver) |
| AUDUSD | 10% | Commodity FX |
| EURJPY | 12% | JPY cross |
| USDJPY | 12% | JPY core |

---

## Risk Calculation Formula

```
risk_amount = balance Ã allocation_pct Ã risk_pct
```

### $100 account examples

| Symbol | Alloc | NORMAL risk | AGGRESSIVE risk |
|--------|-------|-------------|-----------------|
| XAUUSD | 15% | $0.50* | $0.50* |
| USDCHF | 15% | $0.50* | $0.50* |
| GBPUSD | 12% | $0.50* | $0.50* |
| EURUSD | 12% | $0.50* | $0.50* |
| XAGUSD | 12% | $0.50* | $0.50* |
| AUDUSD | 10% | $0.50* | $0.50* |
| EURJPY | 12% | $0.50* | $0.50* |
| USDJPY | 12% | $0.50* | $0.50* |

*Small-balance guard enforces $0.50 minimum (raw calc < $0.50 on $100)

### $1,000 account examples

| Symbol | Alloc | NORMAL risk | AGGRESSIVE risk |
|--------|-------|-------------|-----------------|
| XAUUSD | 15% | $1.50 | $4.50 |
| USDCHF | 15% | $1.50 | $4.50 |
| GBPUSD | 12% | $1.20 | $3.60 |
| EURUSD | 12% | $1.20 | $3.60 |

---

## Expected Log Output (per trade)

```
ð° XAUUSD: Dalio Allocation System  [NORMAL]
   Portfolio Balance:  $100.00  (SMALL  -  <$500)
   Asset Allocation:   15% = $15.00
   Risk Per Trade:     3.33% of allocated = $0.50
   Dynamic DD Cap:     40.0%  (scales 40%->10% NORMAL / 60%->20% AGGRESSIVE from $100 to $2000)

ð DD CHECK [NORMAL]: Balance=$100.00 | Equity=$98.50 | DD=1.5% | Dynamic Cap=40.0%
```

---

## Verification Formula

```python
# Verify any trade manually:
allocated = balance * ASSET_ALLOCATIONS[symbol]
risk      = allocated * risk_pct          # 0.01 NORMAL / 0.03 AGGRESSIVE
dd_cap    = _compute_dynamic_dd_cap(balance, cap_high, cap_floor)
```

---

**Full documentation:** [DALIO_ALLOCATION_SYSTEM.md](DALIO_ALLOCATION_SYSTEM.md)
