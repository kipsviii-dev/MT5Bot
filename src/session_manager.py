"""Session Manager - ICT Kill Zone & Market Context Engine
==========================================================
Provides real-time session detection, ICT kill zone logic, volume/volatility
filters, and 4H trend filtering for both Normal and Aggressive trading modes.

ICT KILL ZONES (UTC):
  - Asia Kill Zone:     00:00 - 04:00 UTC  (Tokyo open, stop hunts)
  - London Kill Zone:   07:00 - 09:00 UTC  (London open, high-probability reversals)
  - NY AM Kill Zone:    12:00 - 15:00 UTC  (NY open, overlap with London close)
  - NY PM Kill Zone:    19:00 - 21:00 UTC  (NY close, reduced liquidity)
  - London Close:       14:30 - 16:30 UTC  (institutional profit-taking)

TRADING MODES:
  - NORMAL:     Trades only during London / NY AM kill zones. Requires 4H trend
                alignment and strict ATR/volatility thresholds. Max 1 position.
  - AGGRESSIVE: Trades all four kill zones. Allows up to MAX_AGGRESSIVE_POSITIONS
                concurrent positions (layered). Uses softer filters and dynamic
                risk with breakeven / de-risk logic.

VOLATILITY CONTEXT:
  - adr_ok:   Average Daily Range check (reject near-zero and blow-off extremes).
  - spread_ok: Broker spread relative to ADR (reject during fat-spread events).
  - volume_ok: Tick volume relative to rolling 20-bar mean (reject if dead market).
"""

from __future__ import annotations
from datetime import datetime, time as dtime, timezone, timedelta
from dataclasses import dataclass, field
from typing import Optional, Tuple
import math


# ─────────────────────────────────────────────────────────────────────────────
# KILL ZONE DEFINITIONS  (UTC hour ranges, inclusive start / exclusive end)
# ─────────────────────────────────────────────────────────────────────────────

KILL_ZONES: dict[str, tuple[int, int]] = {
    "ASIA":          (0,  4),   # 00:00 – 04:00 UTC
    "LONDON_OPEN":   (7,  9),   # 07:00 – 09:00 UTC
    "NY_AM":         (12, 15),  # 12:00 – 15:00 UTC  (London/NY overlap)
    "LONDON_CLOSE":  (14, 17),  # 14:00 – 17:00 UTC  (profit taking)
    "NY_PM":         (19, 21),  # 19:00 – 21:00 UTC  (NY close)
}

# Kill zones allowed per mode
NORMAL_MODE_ZONES:     tuple[str, ...] = ("LONDON_OPEN", "NY_AM")
AGGRESSIVE_MODE_ZONES: tuple[str, ...] = ("ASIA", "LONDON_OPEN", "NY_AM", "LONDON_CLOSE", "NY_PM")


# ─────────────────────────────────────────────────────────────────────────────
# MODE CONSTANTS
# ─────────────────────────────────────────────────────────────────────────────

class TradingMode:
    NORMAL     = "NORMAL"
    AGGRESSIVE = "AGGRESSIVE"


# ─────────────────────────────────────────────────────────────────────────────
# SESSION CONTEXT DATACLASS
# ─────────────────────────────────────────────────────────────────────────────

@dataclass
class SessionContext:
    """Snapshot of current market context evaluated each bar."""
    dt:                 datetime
    utc_hour:           int
    utc_minute:         int

    # Kill zone flags
    active_kill_zone:   Optional[str]   = None   # e.g. "LONDON_OPEN"
    in_normal_zone:     bool            = False
    in_aggressive_zone: bool            = False

    # Volatility / quality
    current_atr:        float           = 0.0
    adr_pct:            float           = 0.0    # ADR as % of price
    volume_ratio:       float           = 1.0    # tick_vol / 20-bar mean
    spread_pips:        float           = 0.0

    adr_ok:             bool            = True
    volume_ok:          bool            = True
    spread_ok:          bool            = True

    # 4H trend
    htf_trend:          str             = "NEUTRAL"   # "BULLISH" / "BEARISH" / "NEUTRAL"
    htf_trend_strength: float           = 0.0         # 0–1

    # Mode evaluation
    mode:               str             = TradingMode.NORMAL
    trade_allowed:      bool            = False
    block_reason:       str             = ""

    def summary(self) -> str:
        kz = self.active_kill_zone or "NONE"
        return (
            f"[{self.dt.strftime('%Y-%m-%d %H:%M')} UTC] "
            f"KZ={kz} | Mode={self.mode} | 4H={self.htf_trend} | "
            f"ATR={self.current_atr:.5f} | VolRatio={self.volume_ratio:.2f} | "
            f"SpreadPips={self.spread_pips:.1f} | "
            f"Trade={'✅ YES' if self.trade_allowed else '❌ NO – ' + self.block_reason}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# MAIN SESSION MANAGER
# ─────────────────────────────────────────────────────────────────────────────

class SessionManager:
    """Evaluates every 5-min bar and returns a SessionContext.

    Usage (Backtrader strategy):
        self.session_mgr = SessionManager(mode=TradingMode.NORMAL)
        ...
        ctx = self.session_mgr.evaluate(
            dt        = bt.num2date(self.data.datetime[0]),
            atr       = float(self.atr[0]),
            close     = float(self.data.close[0]),
            tick_vol  = float(self.data.volume[0]),
            spread_pips = 0.0,          # live: from MT5 symbol info
            htf_ema_fast  = htf_fast,   # 4H EMA values  (pass 0 to disable)
            htf_ema_slow  = htf_slow,
        )
        if ctx.trade_allowed:
            ...
    """

    # ── volatility thresholds ─────────────────────────────────────────────
    ADR_MIN_PCT         = 0.003    # 0.3 % of price  (reject dead market)
    ADR_MAX_PCT         = 0.030    # 3.0 % of price  (reject blow-off)
    VOLUME_RATIO_MIN    = 0.40     # must be ≥40 % of 20-bar mean
    SPREAD_MAX_PIPS     = 4.0      # reject if spread > 4 pips (EURUSD)

    # ── normal mode ATR bounds (5-min) ───────────────────────────────────
    NORMAL_ATR_MIN      = 0.000120
    NORMAL_ATR_MAX      = 0.000600

    # ── aggressive mode ATR bounds ────────────────────────────────────────
    AGGRESSIVE_ATR_MIN  = 0.000080
    AGGRESSIVE_ATR_MAX  = 0.000800

    # ── 4H trend: ratio of fast/slow EMA to declare trend ─────────────────
    HTF_TREND_THRESHOLD = 0.0002   # 2 pips difference = trend declaration

    def __init__(
        self,
        mode: str = TradingMode.NORMAL,
        custom_kill_zones: Optional[dict] = None,
        verbose: bool = False,
    ):
        self.mode    = mode
        self.verbose = verbose

        # Allow override of kill zone table (e.g. for DST adjustments)
        self._kz = custom_kill_zones or KILL_ZONES

        # Rolling volume buffer (20 bars)
        self._vol_buffer: list[float] = []
        self._vol_window = 20

    # ── public API ────────────────────────────────────────────────────────

    def set_mode(self, mode: str) -> None:
        """Switch mode at runtime (e.g. from GUI)."""
        if mode not in (TradingMode.NORMAL, TradingMode.AGGRESSIVE):
            raise ValueError(f"Unknown mode: {mode}")
        self.mode = mode

    def evaluate(
        self,
        dt: datetime,
        atr: float,
        close: float,
        tick_vol: float = 1.0,
        spread_pips: float = 0.0,
        htf_ema_fast: float = 0.0,
        htf_ema_slow: float = 0.0,
        adr_value: float = 0.0,      # pre-calculated ADR; 0 = derive from ATR proxy
    ) -> SessionContext:
        """Evaluate the current bar and return a fully-populated SessionContext."""

        # Normalise to UTC naive datetime
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

        ctx = SessionContext(
            dt          = dt,
            utc_hour    = dt.hour,
            utc_minute  = dt.minute,
            current_atr = atr,
            spread_pips = spread_pips,
            mode        = self.mode,
        )

        # 1. Kill zone detection
        ctx.active_kill_zone   = self._detect_kill_zone(dt)
        ctx.in_normal_zone     = ctx.active_kill_zone in NORMAL_MODE_ZONES
        ctx.in_aggressive_zone = ctx.active_kill_zone in AGGRESSIVE_MODE_ZONES

        # 2. Volatility checks
        ctx = self._check_volatility(ctx, atr, close, tick_vol, spread_pips, adr_value)

        # 3. 4H trend
        ctx = self._check_htf_trend(ctx, htf_ema_fast, htf_ema_slow, close)

        # 4. Final trade gate
        ctx = self._evaluate_trade_permission(ctx)

        if self.verbose:
            print(ctx.summary())

        return ctx

    # ── kill zone helpers ─────────────────────────────────────────────────

    def _detect_kill_zone(self, dt: datetime) -> Optional[str]:
        """Return the name of the highest-priority active kill zone, or None."""
        h = dt.hour
        # Priority: NY_AM > LONDON_OPEN > LONDON_CLOSE > ASIA > NY_PM
        for name in ("NY_AM", "LONDON_OPEN", "LONDON_CLOSE", "ASIA", "NY_PM"):
            start, end = self._kz[name]
            if start <= h < end:
                return name
        return None

    def get_kill_zone_name(self, dt: datetime) -> str:
        """Human-readable kill zone name for the given UTC datetime."""
        kz = self._detect_kill_zone(dt)
        return kz if kz else "OUT_OF_ZONE"

    def is_in_any_kill_zone(self, dt: datetime) -> bool:
        return self._detect_kill_zone(dt) is not None

    def is_in_normal_mode_zone(self, dt: datetime) -> bool:
        return self._detect_kill_zone(dt) in NORMAL_MODE_ZONES

    def is_in_aggressive_mode_zone(self, dt: datetime) -> bool:
        return self._detect_kill_zone(dt) in AGGRESSIVE_MODE_ZONES

    # ── volatility helpers ────────────────────────────────────────────────

    def _check_volatility(
        self,
        ctx: SessionContext,
        atr: float,
        close: float,
        tick_vol: float,
        spread_pips: float,
        adr_value: float,
    ) -> SessionContext:

        # ── ADR check ─────────────────────────────────────────────────────
        if adr_value > 0 and close > 0:
            ctx.adr_pct = adr_value / close
        elif atr > 0 and close > 0:
            # Proxy: ADR ≈ ATR × 4.5 (4.5 × ATR_5m is a reasonable daily proxy)
            ctx.adr_pct = (atr * 4.5) / close
        else:
            ctx.adr_pct = 0.0

        ctx.adr_ok = self.ADR_MIN_PCT <= ctx.adr_pct <= self.ADR_MAX_PCT

        # ── Volume ratio ──────────────────────────────────────────────────
        self._vol_buffer.append(tick_vol)
        if len(self._vol_buffer) > self._vol_window:
            self._vol_buffer.pop(0)

        if len(self._vol_buffer) >= 5:
            mean_vol = sum(self._vol_buffer) / len(self._vol_buffer)
            ctx.volume_ratio = tick_vol / mean_vol if mean_vol > 0 else 1.0
        else:
            ctx.volume_ratio = 1.0  # not enough data yet – assume ok

        ctx.volume_ok = ctx.volume_ratio >= self.VOLUME_RATIO_MIN

        # ── Spread check ──────────────────────────────────────────────────
        ctx.spread_pips = spread_pips
        ctx.spread_ok   = spread_pips <= self.SPREAD_MAX_PIPS

        return ctx

    # ── 4H trend helpers ──────────────────────────────────────────────────

    def _check_htf_trend(
        self,
        ctx: SessionContext,
        fast: float,
        slow: float,
        close: float,
    ) -> SessionContext:
        """Determine 4H trend from two HTF EMA values.

        If both are zero the check is skipped (trend = NEUTRAL, strength = 0).
        """
        if fast == 0.0 and slow == 0.0:
            ctx.htf_trend          = "NEUTRAL"
            ctx.htf_trend_strength = 0.0
            return ctx

        diff = fast - slow
        ctx.htf_trend_strength = min(abs(diff) / self.HTF_TREND_THRESHOLD, 1.0)

        if diff > self.HTF_TREND_THRESHOLD:
            ctx.htf_trend = "BULLISH"
        elif diff < -self.HTF_TREND_THRESHOLD:
            ctx.htf_trend = "BEARISH"
        else:
            ctx.htf_trend = "NEUTRAL"

        return ctx

    # ── gate logic ────────────────────────────────────────────────────────

    def _evaluate_trade_permission(self, ctx: SessionContext) -> SessionContext:
        """Apply all mode-specific rules and set ctx.trade_allowed / block_reason."""

        reasons: list[str] = []

        if ctx.mode == TradingMode.NORMAL:
            # ── NORMAL MODE RULES ─────────────────────────────────────────
            if not ctx.in_normal_zone:
                reasons.append(
                    f"Not in Normal-mode kill zone ({ctx.active_kill_zone or 'NO_ZONE'})"
                )

            if ctx.htf_trend == "BEARISH":
                reasons.append("4H trend is BEARISH (NORMAL mode blocks counter-trend longs)")

            if not (self.NORMAL_ATR_MIN <= ctx.current_atr <= self.NORMAL_ATR_MAX):
                reasons.append(
                    f"ATR {ctx.current_atr:.5f} outside Normal range "
                    f"[{self.NORMAL_ATR_MIN:.5f}, {self.NORMAL_ATR_MAX:.5f}]"
                )

        else:
            # ── AGGRESSIVE MODE RULES ─────────────────────────────────────
            if not ctx.in_aggressive_zone:
                reasons.append(
                    f"Not in Aggressive-mode kill zone ({ctx.active_kill_zone or 'NO_ZONE'})"
                )

            if not (self.AGGRESSIVE_ATR_MIN <= ctx.current_atr <= self.AGGRESSIVE_ATR_MAX):
                reasons.append(
                    f"ATR {ctx.current_atr:.5f} outside Aggressive range "
                    f"[{self.AGGRESSIVE_ATR_MIN:.5f}, {self.AGGRESSIVE_ATR_MAX:.5f}]"
                )

        # ── shared quality gates ──────────────────────────────────────────
        if not ctx.adr_ok:
            reasons.append(f"ADR% {ctx.adr_pct:.4f} outside bounds")

        if not ctx.volume_ok:
            reasons.append(f"Volume ratio {ctx.volume_ratio:.2f} < {self.VOLUME_RATIO_MIN}")

        if not ctx.spread_ok:
            reasons.append(f"Spread {ctx.spread_pips:.1f} pips > max {self.SPREAD_MAX_PIPS}")

        ctx.trade_allowed = len(reasons) == 0
        ctx.block_reason  = "; ".join(reasons) if reasons else ""

        return ctx

    # ── utility ───────────────────────────────────────────────────────────

    @staticmethod
    def format_next_kill_zone(dt: datetime) -> str:
        """Return a human-readable string showing how far to the next kill zone."""
        if dt.tzinfo is not None:
            dt = dt.astimezone(timezone.utc).replace(tzinfo=None)

        h = dt.hour
        upcoming: list[tuple[int, str]] = []
        for name, (start, _) in KILL_ZONES.items():
            hours_to = (start - h) % 24
            upcoming.append((hours_to, name))

        upcoming.sort()
        nearest_h, nearest_name = upcoming[0]
        return f"Next kill zone: {nearest_name} in ~{nearest_h}h"
