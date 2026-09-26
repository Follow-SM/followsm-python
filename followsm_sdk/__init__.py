"""followsm-sdk — official Python client for the FollowSM API."""

from .client import FollowSMClient
from .exceptions import AuthenticationError, FollowSMError, RateLimitExceededException
from .models import (
    BinanceMicrostructureMetrics,
    CompositeSignals,
    ConfluenceSnapshot,
    OrderBookDepthBand,
    PolymarketEventConfluence,
    PolymarketEventMetrics,
    RiskConfig,
    SymbolToxicityMetrics,
    evaluate_risk_action,
)

__all__ = [
    "FollowSMClient",
    "FollowSMError",
    "RateLimitExceededException",
    "AuthenticationError",
    "SymbolToxicityMetrics",
    "OrderBookDepthBand",
    "ConfluenceSnapshot",
    "BinanceMicrostructureMetrics",
    "PolymarketEventConfluence",
    "PolymarketEventMetrics",
    "CompositeSignals",
    "RiskConfig",
    "evaluate_risk_action",
]

__version__ = "1.4.0"
