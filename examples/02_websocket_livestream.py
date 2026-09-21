"""Example: stream live toxicity snapshots over the WebSocket feed."""

import asyncio

from followsm_sdk import FollowSMClient


async def main() -> None:
    client = FollowSMClient(api_key="fsm_live_your_key_here")
    async for snapshot in client.stream_toxicity():
        print(f"{snapshot.symbol}: vpin={snapshot.vpin:.3f} toxic={snapshot.is_toxic_alert}")


if __name__ == "__main__":
    asyncio.run(main())
