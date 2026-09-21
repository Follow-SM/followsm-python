import pytest

from followsm_sdk import FollowSMClient, RateLimitExceededException
from followsm_sdk.exceptions import AuthenticationError


def _mock_response(mocker, status_code, json_data=None, headers=None, text=""):
    response = mocker.Mock()
    response.status_code = status_code
    response.headers = headers or {}
    response.content = b"1" if json_data is not None else b""
    response.text = text
    response.json.return_value = json_data or {}
    if status_code < 400:
        response.raise_for_status.return_value = None
    return response


SNAPSHOT_JSON = {
    "symbol": "BTCUSDT",
    "timestamp": 1.0,
    "price": 60000.0,
    "vpin": 0.85,
    "ob_toxicity_1pct": 1.0,
    "ob_imbalance_l1": 0.5,
    "depth_bands": {
        "0.5%": {"bid_notional": 1.0, "ask_notional": 1.0, "imbalance_ratio": 0.5}
    },
    "volume_z_score": 0.1,
    "natr_15m": 0.1,
    "taker_buy_ratio": 0.5,
    "is_toxic_alert": True,
}


def test_get_toxicity_snapshot_parses_schema(mocker):
    response = _mock_response(mocker, 200, SNAPSHOT_JSON)
    mocker.patch("followsm_sdk.client.requests.get", return_value=response)

    client = FollowSMClient(api_key="fsm_live_test")
    snapshot = client.get_toxicity_snapshot("BTCUSDT")

    assert snapshot.symbol == "BTCUSDT"
    assert snapshot.vpin == 0.85
    assert snapshot.is_toxic_alert is True


def test_get_toxicity_snapshot_raises_rate_limit_exception(mocker):
    response = _mock_response(
        mocker,
        429,
        {"detail": "Rate limit exceeded"},
        headers={"X-RateLimit-Reset": "1726915000"},
    )
    mocker.patch("followsm_sdk.client.requests.get", return_value=response)

    client = FollowSMClient()
    with pytest.raises(RateLimitExceededException) as exc_info:
        client.get_toxicity_snapshot("BTCUSDT")
    assert exc_info.value.reset_time == 1726915000


def test_get_toxicity_snapshot_raises_authentication_error(mocker):
    response = _mock_response(mocker, 401, text="Invalid API key")
    mocker.patch("followsm_sdk.client.requests.get", return_value=response)

    client = FollowSMClient(api_key="bad-key")
    with pytest.raises(AuthenticationError):
        client.get_toxicity_snapshot("BTCUSDT")


def test_default_api_key_is_none():
    client = FollowSMClient()
    assert client.api_key is None
