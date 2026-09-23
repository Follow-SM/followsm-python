"""Example: query a Cross-Venue Confluence snapshot (Binance × Polymarket) for BTCUSDT."""

from followsm_sdk import FollowSMClient, RateLimitExceededException

client = FollowSMClient(api_key="fsm_live_your_key_here")  # omit api_key to use the free tier

try:
    snapshot = client.get_confluence_snapshot("BTCUSDT")
    event = snapshot.polymarket_confluence.active_events[0] if snapshot.polymarket_confluence.active_events else None
    print(f"{snapshot.symbol}: vpin={snapshot.binance_microstructure.vpin:.3f}")
    print(f"  macro_event_risk_score={snapshot.polymarket_confluence.macro_event_risk_score:.2f}")
    print(f"  recommended_action={snapshot.composite_signals.recommended_action}")
    if event:
        print(f"  {event.market_slug}: implied_probability={event.implied_probability:.2f}")
except RateLimitExceededException as exc:
    print(exc)
