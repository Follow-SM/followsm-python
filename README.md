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

## Free vs Developer API

| | Free / Unauthenticated | DEVELOPER_API ($199/mo) |
|---|---|---|
| Requests/min | 30 | 300 |
| WebSocket connections | 1 | Multiple |
| Binance pairs | Limited | 50+ |
| Latency | Standard | Sub-10ms in-memory snapshots |

On HTTP 429, the SDK raises `RateLimitExceededException` with an upgrade prompt pointing to https://follow-sm.com/pricing.
