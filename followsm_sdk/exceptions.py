"""Custom exceptions raised by the FollowSM SDK."""


class FollowSMError(Exception):
    """Base class for all FollowSM SDK errors."""


class RateLimitExceededException(FollowSMError):
    def __init__(self, message: str, reset_time: int):
        self.reset_time = reset_time
        upgrade_url = "https://follow-sm.com/pricing"
        formatted_msg = (
            f"\n\033[91m[FollowSM RateLimitExceeded]\033[0m {message}\n"
            f"\033[93m⚡️ Free Tier Limit Reached (30 req/min).\033[0m\n"
            f"Unlock 300 req/min, 50+ Binance pairs & sub-10ms latency:\n"
            f"👉 \033[94m{upgrade_url}\033[0m\n"
        )
        super().__init__(formatted_msg)


class AuthenticationError(FollowSMError):
    """Raised on HTTP 401/403 responses (invalid key or insufficient plan)."""
