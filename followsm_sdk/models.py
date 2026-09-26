"""Pydantic data models mirroring backend/models/toxicity_models.py."""

from __future__ import annotations

from typing import Dict, List, Literal, Optional

from pydantic import BaseModel


class OrderBookDepthBand(BaseModel):
    bid_notional: float
    ask_notional: float
    imbalance_ratio: float


class SymbolToxicityMetrics(BaseModel):
    symbol: str
    timestamp: float
    price: float
    vpin: float
    # Rank of vpin within this symbol's own recent history [0, 1]; None while warming up.
    vpin_percentile: Optional[float] = None
    ob_toxicity_1pct: float
    ob_imbalance_l1: float
    depth_bands: Dict[str, OrderBookDepthBand]
    volume_z_score: float
    natr_15m: float
    taker_buy_ratio: float
    is_toxic_alert: bool


# ── Cross-Venue Confluence (Binance microstructure × Polymarket event flow) ───


class BinanceMicrostructureMetrics(BaseModel):
    price: float
    vpin: float
    vpin_percentile: Optional[float] = None
    ob_toxicity_1pct: float
    ob_imbalance_l1: float
    depth_bands: Dict[str, OrderBookDepthBand]
    volume_z_score: float
    natr_15m: float
    taker_buy_ratio: float
    price_delta_15m_pct: float


class PolymarketEventMetrics(BaseModel):
    market_slug: str
    question: str
    condition_id: str
    yes_token_id: str
    direction: Literal["bullish_if_yes", "bearish_if_yes", "neutral"]
    direction_confidence: float
    implied_probability: float
    prob_delta_15m: float
    clob_order_flow_imbalance: float
    smart_money_whale_sweeps_1h_usdt: float


class PolymarketEventConfluence(BaseModel):
    active_events: List[PolymarketEventMetrics]
    macro_event_risk_score: float


class CompositeSignals(BaseModel):
    is_toxic_alert: bool
    cross_market_divergence_flag: bool
    recommended_action: Literal["NONE", "WIDEN_SPREAD_1_5X", "WIDEN_SPREAD_2X", "HALT_MAKER_QUOTES"]
    direction_ambiguous: bool = False


class ConfluenceSnapshot(BaseModel):
    """Top-level composite payload from /developer/confluence/*."""

    symbol: str
    timestamp_ms: int
    binance_microstructure: BinanceMicrostructureMetrics
    polymarket_confluence: PolymarketEventConfluence
    composite_signals: CompositeSignals


# ── Client-side risk ladder (quant clients can override the backend's thresholds) ──


class RiskConfig(BaseModel):
    """Custom thresholds for `evaluate_risk_action`, overriding the backend's defaults.

    The percentile thresholds apply whenever the snapshot carries `vpin_percentile`;
    the raw `vpin_*` thresholds are the fallback while the backend is still warming up.
    """

    vpin_percentile_widen_threshold: float = 0.90
    vpin_percentile_halt_threshold: float = 0.95
    # Raw fallback: only extreme readings act while vpin_percentile is unavailable.
    vpin_widen_threshold: float = 0.80
    vpin_halt_threshold: float = 0.90
    ob_toxicity_threshold: float = 2.0
    min_semantic_confidence: float = 0.65


def evaluate_risk_action(snapshot: ConfluenceSnapshot, config: Optional[RiskConfig] = None) -> str:
    """Re-derive a recommended action from `snapshot`'s raw metrics using custom thresholds.

    Mirrors the backend's HFT risk ladder but lets clients pick their own VPIN triggers;
    HALT_MAKER_QUOTES is never returned when the divergence rests on a market whose
    direction_confidence is below `config.min_semantic_confidence`.
    """
    config = config or RiskConfig()
    micro = snapshot.binance_microstructure
    if micro.vpin_percentile is not None:
        level = micro.vpin_percentile
        widen, halt = config.vpin_percentile_widen_threshold, config.vpin_percentile_halt_threshold
    else:
        level, widen, halt = micro.vpin, config.vpin_widen_threshold, config.vpin_halt_threshold
    toxic_book = micro.ob_toxicity_1pct > config.ob_toxicity_threshold
    divergence = snapshot.composite_signals.cross_market_divergence_flag
    min_confidence = min(
        (e.direction_confidence for e in snapshot.polymarket_confluence.active_events),
        default=1.0,
    )
    if (level >= halt or toxic_book) and divergence:
        if min_confidence < config.min_semantic_confidence:
            return "WIDEN_SPREAD_1_5X"
        return "HALT_MAKER_QUOTES"
    if level >= widen or toxic_book:
        return "WIDEN_SPREAD_2X"
    if divergence:
        return "WIDEN_SPREAD_1_5X"
    return "NONE"
