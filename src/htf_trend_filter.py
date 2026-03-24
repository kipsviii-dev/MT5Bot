"""HTF (Higher Time-Frame) Trend Filter - 4H EMA Trend Engine
=============================================================
Provides a lightweight 4H EMA trend signal that can be used by any 5-min
strategy to block counter-trend entries in NORMAL mode.

Two approaches are supported:

1. LIVE (MT5 / real-time):
   Call HTFTrendFilter.from_mt5_bars() to fetch 4H bars from MT5 and compute
   the EMAs inside this class.

2. BACKTEST (Backtrader):
   Feed 4H OHLCV data into HTFTrendFilter.update_bar() bar-by-bar, then call
   get_trend() to read the current signal.  Alternatively, if you don't have
   separate 4H data, use HTFTrendFilter.resample_from_m5_bars() with a rolling
   buffer of 5-min closes.

OUTPUTS:
    trend   : "BULLISH" | "BEARISH" | "NEUTRAL"
    strength: 0.0 – 1.0  (how far fast EMA is above/below slow EMA as % of price)
    ema_fast: current value of fast EMA on 4H chart
    ema_slow: current value of slow EMA on 4H chart
"""

from __future__ import annotations
from typing import List, Optional, Deque
from collections import deque
import math


# ─────────────────────────────────────────────────────────────────────────────
# EMA calculator (no external deps)
# ─────────────────────────────────────────────────────────────────────────────

def _ema(period: int, values: List[float]) -> List[float]:
    """Return a list of EMA values the same length as `values`.
    The first `period-1` values are NaN.
    """
    if not values or period <= 0:
        return []
    k = 2.0 / (period + 1)
    result: List[float] = [math.nan] * len(values)
    # seed with simple average
    for i in range(period - 1, len(values)):
        if i == period - 1:
            result[i] = sum(values[i - period + 1: i + 1]) / period
        else:
            result[i] = values[i] * k + result[i - 1] * (1 - k)
    return result


# ─────────────────────────────────────────────────────────────────────────────
# HTF TREND FILTER
# ─────────────────────────────────────────────────────────────────────────────

class HTFTrendFilter:
    """Incremental 4H EMA trend filter.

    Parameters
    ----------
    fast_period : int
        Fast EMA period on the 4H chart (default 21).
    slow_period : int
        Slow EMA period on the 4H chart (default 50).
    threshold_pct : float
        Minimum (fast-slow)/price ratio to declare a non-NEUTRAL trend.
        Default 0.0005 = 0.05 % separation.
    m5_bars_per_h4 : int
        How many 5-min bars make one 4H bar (48 for strict 4H, use 48).
    """

    DEFAULT_FAST_PERIOD  = 21
    DEFAULT_SLOW_PERIOD  = 50
    DEFAULT_THRESHOLD    = 0.0005   # 0.05 % of price

    def __init__(
        self,
        fast_period:     int   = DEFAULT_FAST_PERIOD,
        slow_period:     int   = DEFAULT_SLOW_PERIOD,
        threshold_pct:   float = DEFAULT_THRESHOLD,
        m5_bars_per_h4:  int   = 48,
    ):
        self.fast_period    = fast_period
        self.slow_period    = slow_period
        self.threshold_pct  = threshold_pct
        self.m5_per_h4      = m5_bars_per_h4

        # Incremental EMA state
        self._ema_fast: Optional[float] = None
        self._ema_slow: Optional[float] = None
        self._k_fast = 2.0 / (fast_period + 1)
        self._k_slow = 2.0 / (slow_period + 1)

        # Seed buffers (for first EMA calculation)
        self._seed_buf_fast: List[float] = []
        self._seed_buf_slow: List[float] = []
        self._bars_seen = 0

        # 5-min → 4H resampler
        self._m5_buf: Deque[float] = deque(maxlen=m5_bars_per_h4)

    # ── public API ────────────────────────────────────────────────────────

    def update_h4_close(self, close: float) -> None:
        """Feed one completed 4H bar close price."""
        self._bars_seen += 1
        self._update_ema(close)

    def update_m5_close(self, close: float) -> bool:
        """Feed one 5-min close.  Returns True when a new 4H bar is formed.

        Use this for backtest where only 5-min data is available.
        A synthetic 4H bar is formed every `m5_bars_per_h4` bars.
        """
        self._m5_buf.append(close)
        if len(self._m5_buf) == self._m5_buf.maxlen:
            h4_close = list(self._m5_buf)[-1]   # last 5-min close of the 4H bar
            self.update_h4_close(h4_close)
            return True
        return False

    def get_trend(self, current_close: float = 0.0) -> dict:
        """Return current trend state.

        Returns
        -------
        dict with keys: trend, strength, ema_fast, ema_slow, ready
        """
        fast = self._ema_fast
        slow = self._ema_slow
        ref  = current_close if current_close > 0 else (fast or 1.0)

        if fast is None or slow is None or math.isnan(fast) or math.isnan(slow):
            return {
                'trend':    'NEUTRAL',
                'strength': 0.0,
                'ema_fast': 0.0,
                'ema_slow': 0.0,
                'ready':    False,
            }

        diff = fast - slow
        strength = min(abs(diff) / (ref * self.threshold_pct), 1.0) if ref > 0 else 0.0

        if diff > ref * self.threshold_pct:
            trend = 'BULLISH'
        elif diff < -(ref * self.threshold_pct):
            trend = 'BEARISH'
        else:
            trend = 'NEUTRAL'

        return {
            'trend':    trend,
            'strength': strength,
            'ema_fast': fast,
            'ema_slow': slow,
            'ready':    True,
        }

    def is_bullish(self, current_close: float = 0.0) -> bool:
        return self.get_trend(current_close)['trend'] == 'BULLISH'

    def is_bearish(self, current_close: float = 0.0) -> bool:
        return self.get_trend(current_close)['trend'] == 'BEARISH'

    def is_ready(self) -> bool:
        """True once enough bars have been seen to produce valid EMAs."""
        return self._bars_seen >= self.slow_period

    def reset(self) -> None:
        """Clear all state (e.g. when reconnecting live data)."""
        self._ema_fast = None
        self._ema_slow = None
        self._seed_buf_fast.clear()
        self._seed_buf_slow.clear()
        self._bars_seen = 0
        self._m5_buf.clear()

    # ── incremental EMA helper ────────────────────────────────────────────

    def _update_ema(self, close: float) -> None:
        # Fast EMA
        if self._ema_fast is None:
            self._seed_buf_fast.append(close)
            if len(self._seed_buf_fast) >= self.fast_period:
                self._ema_fast = sum(self._seed_buf_fast[-self.fast_period:]) / self.fast_period
        else:
            self._ema_fast = close * self._k_fast + self._ema_fast * (1 - self._k_fast)

        # Slow EMA
        if self._ema_slow is None:
            self._seed_buf_slow.append(close)
            if len(self._seed_buf_slow) >= self.slow_period:
                self._ema_slow = sum(self._seed_buf_slow[-self.slow_period:]) / self.slow_period
        else:
            self._ema_slow = close * self._k_slow + self._ema_slow * (1 - self._k_slow)

    # ── bulk initialisation from a list of closes ─────────────────────────

    def seed_from_closes(self, closes: List[float]) -> None:
        """Pre-load historical 4H closes (e.g. from MT5 history fetch)."""
        for c in closes:
            self.update_h4_close(c)

    # ── MT5 integration helper ────────────────────────────────────────────

    @classmethod
    def from_mt5_bars(
        cls,
        symbol:       str,
        fast_period:  int   = DEFAULT_FAST_PERIOD,
        slow_period:  int   = DEFAULT_SLOW_PERIOD,
        threshold_pct: float = DEFAULT_THRESHOLD,
        lookback_bars: int  = 200,
    ) -> 'HTFTrendFilter':
        """Create and seed an HTFTrendFilter from live MT5 4H data.

        Requires MetaTrader5 to be initialised and connected.
        Returns the filter object ready for live use.

        Example
        -------
        htf = HTFTrendFilter.from_mt5_bars('EURUSD')
        trend_info = htf.get_trend(current_close=1.08500)
        """
        try:
            import MetaTrader5 as mt5  # type: ignore

            rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_H4, 0, lookback_bars)
            if rates is None or len(rates) == 0:
                print(f"[HTFTrendFilter] Could not fetch 4H bars for {symbol}")
                return cls(fast_period, slow_period, threshold_pct)

            closes = [float(r['close']) for r in rates]
            instance = cls(fast_period, slow_period, threshold_pct)
            instance.seed_from_closes(closes)
            print(
                f"[HTFTrendFilter] Seeded with {len(closes)} 4H bars for {symbol}. "
                f"Trend: {instance.get_trend(closes[-1])['trend']}"
            )
            return instance

        except ImportError:
            print("[HTFTrendFilter] MetaTrader5 not available – returning unseeded filter")
            return cls(fast_period, slow_period, threshold_pct)
