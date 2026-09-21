# followsm-sdk

Official Python SDK for the [FollowSM](https://follow-sm.com) smart-money & orderbook toxicity API.

## Install

```bash
pip install followsm-sdk
```

## Quickstart

```python
from followsm_sdk import FollowSMClient

client = FollowSMClient(api_key="fsm_live_...")  # or omit to use the free tier
snapshot = client.get_toxicity_snapshot("BTCUSDT")
print(snapshot.vpin, snapshot.is_toxic_alert)
```

## `SymbolToxicityMetrics` response

`get_toxicity_snapshot()` and `get_toxic_pairs()` both return `SymbolToxicityMetrics` (pydantic models), matching the raw JSON the backend returns:

```json
{
  "symbol": "BTCUSDT",
  "timestamp": 1758412800.0,
  "price": 62150.5,
  "vpin": 0.72,
  "ob_toxicity_1pct": 2.35,
  "ob_imbalance_l1": 0.61,
  "depth_bands": {
    "0.5%": { "bid_notional": 184320.0, "ask_notional": 96410.0, "imbalance_ratio": 0.657 },
    "1.0%": { "bid_notional": 312500.0, "ask_notional": 210800.0, "imbalance_ratio": 0.597 },
    "2.0%": { "bid_notional": 590100.0, "ask_notional": 470200.0, "imbalance_ratio": 0.556 }
  },
  "volume_z_score": 3.1,
  "natr_15m": 0.84,
  "taker_buy_ratio": 0.58,
  "is_toxic_alert": true
}
```

| Field | Type | Description |
|---|---|---|
| `symbol` | `str` | Trading pair, e.g. `"BTCUSDT"` |
| `timestamp` | `float` | Unix epoch seconds when the snapshot was computed |
| `price` | `float` | Last traded price |
| `vpin` | `float` | Volume-Synchronized Probability of Informed Trading, `[0.0, 1.0]` |
| `ob_toxicity_1pct` | `float` | Ask/bid notional ratio within ±1% of mid price |
| `ob_imbalance_l1` | `float` | Best bid/ask (L1) imbalance |
| `depth_bands` | `dict[str, OrderBookDepthBand]` | Keyed by band width (`"0.5%"`, `"1.0%"`, `"2.0%"`), each with `bid_notional`, `ask_notional`, `imbalance_ratio` |
| `volume_z_score` | `float` | Robust Z-score of recent traded volume |
| `natr_15m` | `float` | Normalized ATR over 15-minute candles |
| `taker_buy_ratio` | `float` | Share of taker volume that was buy-side |
| `is_toxic_alert` | `bool` | `True` when `vpin > 0.70` or `ob_toxicity_1pct > 2.0` |

## Free vs Developer API

| | Free / Unauthenticated | DEVELOPER_API ($199/mo) |
|---|---|---|
| Requests/min | 30 | 300 |
| WebSocket connections | 1 | Multiple |
| Binance pairs | Limited | 50+ |
| Latency | Standard | Sub-10ms in-memory snapshots |

On HTTP 429, the SDK raises `RateLimitExceededException` with an upgrade prompt pointing to https://follow-sm.com/pricing.

## Live streaming

```python
import asyncio
from followsm_sdk import FollowSMClient

async def main() -> None:
    client = FollowSMClient(api_key="fsm_live_...")
    async for snapshot in client.stream_toxicity():
        print(snapshot.symbol, snapshot.vpin, snapshot.is_toxic_alert)

asyncio.run(main())
```
