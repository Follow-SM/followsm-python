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
    SymbolToxicityMetrics,
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
]

__version__ = "1.1.0"
