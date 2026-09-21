"""Pydantic data models mirroring backend/models/toxicity_models.py."""

from __future__ import annotations

from typing import Dict

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
