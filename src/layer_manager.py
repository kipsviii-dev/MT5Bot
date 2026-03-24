"""Trade Layer Manager - Breakeven, De-risk & Position Layering Engine
=====================================================================
Manages multiple concurrent positions in AGGRESSIVE mode:
  - Tracks each open "layer" with its own entry, SL, TP, and age
  - Applies breakeven logic: move SL to entry once price clears 1.5 × ATR
  - De-risk: close most-vulnerable position (highest unrealised loss first)
    when total floating DD exceeds MAX_FLOATING_DD_PCT of account equity
  - Layering guard: reject new entries when layer count hits cap or total
    exposure exceeds MAX_TOTAL_EXPOSURE_PCT

NORMAL mode: always 1 layer, no layering logic applied.
AGGRESSIVE mode: up to MAX_AGGRESSIVE_LAYERS positions, with full de-risk.

This module is strategy-agnostic – it works with plain Python floats so it can
be unit-tested without Backtrader or MT5.

Usage (Backtrader strategy):
    self.layer_mgr = LayerManager(mode=TradingMode.AGGRESSIVE, account_equity=10000)

    # When entering:
    layer_id = self.layer_mgr.add_layer(
        entry_price=1.08500, stop_price=1.08200, take_price=1.09500,
        lot_size=0.05, current_price=1.08500, atr=0.00030,
    )

    # Each bar – update prices and run management:
    actions = self.layer_mgr.update(current_price=1.08650, account_equity=self.broker.get_value())
    for action in actions:
        if action['type'] == 'MOVE_SL':
            # adjust SL order for action['layer_id'] to action['new_sl']
        elif action['type'] == 'CLOSE_LAYER':
            # close the position for action['layer_id'] (reason: action['reason'])

    # Before entering: check if allowed
    if self.layer_mgr.can_add_layer(current_price, account_equity):
        ...
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Dict, Optional
import time


# ─────────────────────────────────────────────────────────────────────────────
# TRADING MODE CONSTANTS  (mirrors advanced_mt5_monitor_gui.py definitions)
# ─────────────────────────────────────────────────────────────────────────────

TRADING_MODE_NORMAL     = "NORMAL"
TRADING_MODE_AGGRESSIVE = "AGGRESSIVE"

# ─────────────────────────────────────────────────────────────────────────────
# CONSTANTS (mode-specific)
# ─────────────────────────────────────────────────────────────────────────────

MAX_AGGRESSIVE_LAYERS   = 3      # max concurrent positions in AGGRESSIVE mode
MAX_NORMAL_LAYERS       = 1      # always 1 in NORMAL mode

# NORMAL – tight drawdown guard (capital preservation)
MAX_FLOATING_DD_PCT_NORMAL      = 0.03   # 3 % of equity – trigger de-risk
MAX_TOTAL_EXPOSURE_PCT_NORMAL   = 0.06   # 6 % total notional exposure / equity

# AGGRESSIVE – wider drawdown tolerance (max-growth / small-balance bootstrap)
MAX_FLOATING_DD_PCT_AGGRESSIVE  = 0.15   # 15 % of equity – trigger de-risk
MAX_TOTAL_EXPOSURE_PCT_AGGRESSIVE = 0.50  # 50 % total notional exposure / equity

# Keep legacy names as aliases pointing to NORMAL defaults (backward compat)
MAX_FLOATING_DD_PCT    = MAX_FLOATING_DD_PCT_NORMAL
MAX_TOTAL_EXPOSURE_PCT = MAX_TOTAL_EXPOSURE_PCT_NORMAL

BREAKEVEN_ATR_MULTIPLE = 1.5    # move SL to entry when price ≥ entry + 1.5 × ATR
PARTIAL_CLOSE_PCT      = 0.50   # close 50 % of oldest layer on de-risk trigger


# ─────────────────────────────────────────────────────────────────────────────
# LAYER DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class TradeLayer:
    layer_id:       int
    entry_price:    float
    stop_price:     float          # current SL (may be adjusted to BE)
    initial_stop:   float          # original SL (never moves)
    take_price:     float
    lot_size:       float
    entry_atr:      float
    direction:      str            # "LONG" (only LONG supported currently)
    entry_time:     float          = field(default_factory=time.time)
    at_breakeven:   bool           = False
    is_runner:      bool           = False   # last layer kept as "runner"

    @property
    def unrealised_pnl_pips(self) -> float:
        """Approximate unrealised P&L in pips (requires current_price inject)."""
        return 0.0  # placeholder – see LayerManager.update()

    @property
    def risk_pips(self) -> float:
        return abs(self.entry_price - self.initial_stop) / 0.0001

    @property
    def reward_pips(self) -> float:
        return abs(self.take_price - self.entry_price) / 0.0001

    @property
    def rr_ratio(self) -> float:
        return self.reward_pips / self.risk_pips if self.risk_pips > 0 else 0.0


# ─────────────────────────────────────────────────────────────────────────────
# LAYER MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class LayerManager:
    """Manages all open trade layers for a single instrument.

    Mode behaviour:
        NORMAL     – 1 layer max, tight 3% floating DD guard, 6% exposure cap.
        AGGRESSIVE – 3 layers max, 15% floating DD guard, 50% exposure cap
                     (designed for small-account bootstrap / max-growth runs).
    """

    def __init__(self, mode: str = TRADING_MODE_NORMAL, account_equity: float = 10_000.0):
        self.mode            = mode
        self.account_equity  = account_equity
        self._layers:  List[TradeLayer] = []
        self._next_id: int  = 1

    # ── mode-specific limits (properties so they update if self.mode changes) ─

    @property
    def max_floating_dd_pct(self) -> float:
        return (MAX_FLOATING_DD_PCT_AGGRESSIVE
                if self.mode == TRADING_MODE_AGGRESSIVE
                else MAX_FLOATING_DD_PCT_NORMAL)

    @property
    def max_total_exposure_pct(self) -> float:
        return (MAX_TOTAL_EXPOSURE_PCT_AGGRESSIVE
                if self.mode == TRADING_MODE_AGGRESSIVE
                else MAX_TOTAL_EXPOSURE_PCT_NORMAL)

    # ── properties ────────────────────────────────────────────────────────

    @property
    def max_layers(self) -> int:
        return MAX_AGGRESSIVE_LAYERS if self.mode == "AGGRESSIVE" else MAX_NORMAL_LAYERS

    @property
    def layer_count(self) -> int:
        return len(self._layers)

    @property
    def has_open_position(self) -> bool:
        return len(self._layers) > 0

    def get_layers(self) -> List[TradeLayer]:
        return list(self._layers)

    # ── add / remove ──────────────────────────────────────────────────────

    def can_add_layer(self, current_price: float, account_equity: float) -> bool:
        """Return True if a new layer is permitted under current rules."""
        if self.layer_count >= self.max_layers:
            return False

        # Total exposure guard (mode-specific)
        total_notional = sum(
            lyr.lot_size * 100_000 * lyr.entry_price
            for lyr in self._layers
        )
        if account_equity > 0 and (total_notional / account_equity) > self.max_total_exposure_pct * 100:
            return False

        return True

    def add_layer(
        self,
        entry_price:   float,
        stop_price:    float,
        take_price:    float,
        lot_size:      float,
        current_price: float,
        atr:           float,
        direction:     str = "LONG",
    ) -> int:
        """Register a new trade layer.  Returns the assigned layer_id."""
        layer = TradeLayer(
            layer_id      = self._next_id,
            entry_price   = entry_price,
            stop_price    = stop_price,
            initial_stop  = stop_price,
            take_price    = take_price,
            lot_size      = lot_size,
            entry_atr     = atr,
            direction     = direction,
        )
        self._layers.append(layer)
        self._next_id += 1
        return layer.layer_id

    def remove_layer(self, layer_id: int) -> None:
        """Remove a closed/cancelled layer by ID."""
        self._layers = [lyr for lyr in self._layers if lyr.layer_id != layer_id]

    def clear_all(self) -> None:
        """Remove all layers (e.g. on strategy reset)."""
        self._layers.clear()

    # ── main update loop ──────────────────────────────────────────────────

    def update(
        self,
        current_price:  float,
        account_equity: float,
    ) -> List[Dict]:
        """Evaluate all layers and return a list of action dicts.

        Each action dict has at minimum:
            {
                'type':     'MOVE_SL' | 'CLOSE_LAYER' | 'INFO',
                'layer_id': int,
                'reason':   str,
                ...extra keys depending on type...
            }
        """
        self.account_equity = account_equity
        actions: List[Dict] = []

        if not self._layers:
            return actions

        # ── 1. Calculate per-layer unrealised P&L ─────────────────────────
        layer_pnl: Dict[int, float] = {}
        for lyr in self._layers:
            pnl = (current_price - lyr.entry_price) * lyr.lot_size * 100_000
            layer_pnl[lyr.layer_id] = pnl

        # ── 2. Breakeven promotion ─────────────────────────────────────────
        for lyr in self._layers:
            if lyr.at_breakeven or lyr.direction != "LONG":
                continue
            breakeven_trigger = lyr.entry_price + BREAKEVEN_ATR_MULTIPLE * lyr.entry_atr
            if current_price >= breakeven_trigger:
                new_sl = lyr.entry_price + (lyr.entry_atr * 0.2)  # tiny buffer above entry
                if new_sl > lyr.stop_price:
                    lyr.stop_price  = new_sl
                    lyr.at_breakeven = True
                    actions.append({
                        'type':     'MOVE_SL',
                        'layer_id': lyr.layer_id,
                        'new_sl':   new_sl,
                        'reason':   f"Breakeven: price {current_price:.5f} ≥ trigger {breakeven_trigger:.5f}",
                    })

        # ── 3. Individual SL-hit detection ────────────────────────────────
        for lyr in list(self._layers):
            if lyr.direction == "LONG" and current_price <= lyr.stop_price:
                actions.append({
                    'type':     'CLOSE_LAYER',
                    'layer_id': lyr.layer_id,
                    'reason':   f"SL hit at {lyr.stop_price:.5f} (price={current_price:.5f})",
                    'pnl_est':  layer_pnl.get(lyr.layer_id, 0.0),
                })

        # ── 4. TP hit detection ───────────────────────────────────────────
        for lyr in list(self._layers):
            if lyr.direction == "LONG" and current_price >= lyr.take_price:
                actions.append({
                    'type':     'CLOSE_LAYER',
                    'layer_id': lyr.layer_id,
                    'reason':   f"TP hit at {lyr.take_price:.5f} (price={current_price:.5f})",
                    'pnl_est':  layer_pnl.get(lyr.layer_id, 0.0),
                })

        # ── 5. Portfolio-level floating DD de-risk ─────────────────────────
        total_pnl   = sum(layer_pnl.values())
        floating_dd = -total_pnl / account_equity if account_equity > 0 else 0.0

        if floating_dd > self.max_floating_dd_pct and len(self._layers) > 1:
            # Close the most-vulnerable layer (most negative unrealised PnL)
            already_closing_ids = {a['layer_id'] for a in actions if a['type'] == 'CLOSE_LAYER'}
            candidates = [
                lyr for lyr in self._layers
                if lyr.layer_id not in already_closing_ids
                and not lyr.at_breakeven          # prefer closing non-BE layers first
            ]
            if not candidates:
                # Fall back – pick the one with worst PnL
                candidates = [
                    lyr for lyr in self._layers
                    if lyr.layer_id not in already_closing_ids
                ]

            if candidates:
                victim = min(candidates, key=lambda l: layer_pnl.get(l.layer_id, 0.0))
                actions.append({
                    'type':     'CLOSE_LAYER',
                    'layer_id': victim.layer_id,
                    'reason':   (
                        f"DE-RISK [{self.mode}]: floating DD {floating_dd*100:.2f}% > "
                        f"{self.max_floating_dd_pct*100:.0f}% threshold"
                    ),
                    'pnl_est':  layer_pnl.get(victim.layer_id, 0.0),
                })

        # ── 6. Mark runner (last remaining layer never de-risked) ──────────
        live_ids = {a['layer_id'] for a in actions if a['type'] == 'CLOSE_LAYER'}
        survivors = [lyr for lyr in self._layers if lyr.layer_id not in live_ids]
        if len(survivors) == 1:
            survivors[0].is_runner = True

        return actions

    # ── reporting ─────────────────────────────────────────────────────────

    def summary(self, current_price: float) -> str:
        if not self._layers:
            return f"LayerManager [{self.mode}]: No open positions"
        dd_pct_str = f"{self.max_floating_dd_pct*100:.0f}% DD guard"
        lines = [
            f"LayerManager [{self.mode}] ({dd_pct_str}): "
            f"{self.layer_count}/{self.max_layers} layers open"
        ]
        for lyr in self._layers:
            pnl_pips = (current_price - lyr.entry_price) / 0.0001
            be_tag   = " [BE]" if lyr.at_breakeven else ""
            run_tag  = " [RUNNER]" if lyr.is_runner else ""
            lines.append(
                f"  Layer #{lyr.layer_id}{be_tag}{run_tag}: "
                f"Entry={lyr.entry_price:.5f} SL={lyr.stop_price:.5f} "
                f"TP={lyr.take_price:.5f} Lots={lyr.lot_size:.2f} "
                f"PnL={pnl_pips:+.1f} pips"
            )
        return "\n".join(lines)
