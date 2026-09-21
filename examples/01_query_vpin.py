"""Example: query a one-off VPIN / toxicity snapshot for BTCUSDT."""

from followsm_sdk import FollowSMClient, RateLimitExceededException

client = FollowSMClient(api_key="fsm_live_your_key_here")  # omit api_key to use the free tier

try:
    snapshot = client.get_toxicity_snapshot("BTCUSDT")
    print(f"{snapshot.symbol}: vpin={snapshot.vpin:.3f} toxic={snapshot.is_toxic_alert}")
except RateLimitExceededException as exc:
    print(exc)
