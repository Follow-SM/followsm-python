"""followsm-sdk — official Python client for the FollowSM API."""

from .client import FollowSMClient
from .exceptions import AuthenticationError, FollowSMError, RateLimitExceededException
from .models import OrderBookDepthBand, SymbolToxicityMetrics

__all__ = [
    "FollowSMClient",
    "FollowSMError",
    "RateLimitExceededException",
    "AuthenticationError",
    "SymbolToxicityMetrics",
    "OrderBookDepthBand",
]

__version__ = "0.1.0"
