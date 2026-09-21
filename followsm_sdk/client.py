"""Core synchronous + async streaming client for the FollowSM API."""

from __future__ import annotations

import json
from typing import AsyncIterator, List, Optional

import requests
import websockets

from .exceptions import AuthenticationError, RateLimitExceededException
from .models import SymbolToxicityMetrics

DEFAULT_BASE_URL = "https://follow-sm.com/api/v1"
DEFAULT_WS_URL = "wss://follow-sm.com/api/v1/developer/toxicity/stream"


class FollowSMClient:
    """Client for the FollowSM Developer API.

    When `api_key` is omitted, requests are sent unauthenticated and are
    subject to the backend's IP-based free-tier rate limit.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: str = DEFAULT_BASE_URL,
        ws_url: str = DEFAULT_WS_URL,
        timeout: float = 10.0,
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.ws_url = ws_url
        self.timeout = timeout

    def _headers(self) -> dict:
        return {"X-FollowSM-Key": self.api_key} if self.api_key else {}

    def _handle_response(self, response: requests.Response) -> requests.Response:
        if response.status_code == 429:
            reset_time = int(response.headers.get("X-RateLimit-Reset", 0))
            raise RateLimitExceededException(
                response.json().get("detail", "Rate limit exceeded")
                if response.content
                else "Rate limit exceeded",
                reset_time,
            )
        if response.status_code in (401, 403):
            raise AuthenticationError(response.text)
        response.raise_for_status()
        return response

    def get_toxicity_snapshot(self, symbol: str) -> SymbolToxicityMetrics:
        response = requests.get(
            f"{self.base_url}/developer/toxicity/snapshot",
            params={"symbol": symbol},
            headers=self._headers(),
            timeout=self.timeout,
        )
        self._handle_response(response)
        return SymbolToxicityMetrics.model_validate(response.json())

    def get_toxic_pairs(self) -> List[SymbolToxicityMetrics]:
        response = requests.get(
            f"{self.base_url}/developer/toxicity/toxic-pairs",
            headers=self._headers(),
            timeout=self.timeout,
        )
        self._handle_response(response)
        return [SymbolToxicityMetrics.model_validate(item) for item in response.json()]

    async def stream_toxicity(self) -> AsyncIterator[SymbolToxicityMetrics]:
        """Async-iterate live toxicity snapshots over the WebSocket feed."""
        uri = f"{self.ws_url}?api_key={self.api_key}" if self.api_key else self.ws_url
        async with websockets.connect(uri) as ws:
            async for message in ws:
                yield SymbolToxicityMetrics.model_validate(json.loads(message))
