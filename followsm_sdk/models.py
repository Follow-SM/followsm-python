"""Pydantic data models mirroring backend/models/toxicity_models.py."""

from __future__ import annotations

from typing import Dict, List, Literal

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
    direction: Literal["bullish_if_yes", "bearish_if_yes"]
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


class ConfluenceSnapshot(BaseModel):
    """Top-level composite payload from /developer/confluence/*."""

    symbol: str
    timestamp_ms: int
    binance_microstructure: BinanceMicrostructureMetrics
    polymarket_confluence: PolymarketEventConfluence
    composite_signals: CompositeSignals
