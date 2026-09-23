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
    """Custom thresholds for `evaluate_risk_action`, overriding the backend's defaults."""

    vpin_widen_threshold: float = 0.60
    vpin_halt_threshold: float = 0.80
    min_semantic_confidence: float = 0.65


def evaluate_risk_action(snapshot: ConfluenceSnapshot, config: Optional[RiskConfig] = None) -> str:
    """Re-derive a recommended action from `snapshot`'s raw metrics using custom thresholds.

    Mirrors the backend's HFT risk ladder but lets clients pick their own VPIN triggers;
    HALT_MAKER_QUOTES is never returned when the divergence rests on a market whose
    direction_confidence is below `config.min_semantic_confidence`.
    """
    config = config or RiskConfig()
    vpin = snapshot.binance_microstructure.vpin
    divergence = snapshot.composite_signals.cross_market_divergence_flag
    min_confidence = min(
        (e.direction_confidence for e in snapshot.polymarket_confluence.active_events),
        default=1.0,
    )
    if vpin >= config.vpin_halt_threshold and divergence:
        if min_confidence < config.min_semantic_confidence:
            return "WIDEN_SPREAD_1_5X"
        return "HALT_MAKER_QUOTES"
    if vpin >= config.vpin_widen_threshold:
        return "WIDEN_SPREAD_2X"
    if divergence:
        return "WIDEN_SPREAD_1_5X"
    return "NONE"
