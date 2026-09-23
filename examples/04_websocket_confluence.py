"""Example: stream live Cross-Venue Confluence snapshots (Enterprise only)."""

import asyncio

from followsm_sdk import FollowSMClient


async def main() -> None:
    client = FollowSMClient(api_key="fsm_live_your_key_here")
    async for snapshot in client.stream_confluence():
        action = snapshot.composite_signals.recommended_action
        divergent = snapshot.composite_signals.cross_market_divergence_flag
        print(f"{snapshot.symbol}: action={action} divergence={divergent}")


if __name__ == "__main__":
    asyncio.run(main())
