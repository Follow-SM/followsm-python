from followsm_sdk import ConfluenceSnapshot, FollowSMClient, RiskConfig, evaluate_risk_action

_BAND = {"bid_notional": 1.0, "ask_notional": 1.0, "imbalance_ratio": 0.5}


def _snapshot(vpin=0.85, divergence=True, confidence=1.0) -> ConfluenceSnapshot:
    return ConfluenceSnapshot.model_validate(
        {
            "symbol": "BTCUSDT",
            "timestamp_ms": 1,
            "binance_microstructure": {
                "price": 60000.0,
                "vpin": vpin,
                "ob_toxicity_1pct": 1.0,
                "ob_imbalance_l1": 0.5,
                "depth_bands": {"0.5%": _BAND},
                "volume_z_score": 0.1,
                "natr_15m": 0.1,
                "taker_buy_ratio": 0.5,
                "price_delta_15m_pct": 0.01,
            },
            "polymarket_confluence": {
                "active_events": [
                    {
                        "market_slug": "will-btc-hit-70k",
                        "question": "Will Bitcoin hit $70k?",
                        "condition_id": "cond-1",
                        "yes_token_id": "yes-1",
                        "direction": "bullish_if_yes",
                        "direction_confidence": confidence,
                        "implied_probability": 0.6,
                        "prob_delta_15m": 0.09,
                        "clob_order_flow_imbalance": 0.6,
                        "smart_money_whale_sweeps_1h_usdt": 100_000.0,
                    }
                ],
                "macro_event_risk_score": 0.7,
            },
            "composite_signals": {
                "is_toxic_alert": vpin >= 0.7,
                "cross_market_divergence_flag": divergence,
                "recommended_action": "HALT_MAKER_QUOTES" if divergence else "NONE",
                "direction_ambiguous": False,
            },
        }
    )


def test_evaluate_risk_action_defaults_halt_on_high_vpin_and_divergence():
    assert evaluate_risk_action(_snapshot(vpin=0.85, divergence=True)) == "HALT_MAKER_QUOTES"


def test_evaluate_risk_action_downgrades_halt_on_low_confidence():
    snapshot = _snapshot(vpin=0.85, divergence=True, confidence=0.4)
    assert evaluate_risk_action(snapshot) == "WIDEN_SPREAD_1_5X"


def test_evaluate_risk_action_respects_custom_thresholds():
    snapshot = _snapshot(vpin=0.5, divergence=False)
    config = RiskConfig(vpin_widen_threshold=0.4, vpin_halt_threshold=0.9)
    assert evaluate_risk_action(snapshot, config) == "WIDEN_SPREAD_2X"


def test_client_evaluate_risk_uses_its_configured_risk_config():
    client = FollowSMClient(risk_config=RiskConfig(min_semantic_confidence=0.9))
    snapshot = _snapshot(vpin=0.85, divergence=True, confidence=0.8)
    assert client.evaluate_risk(snapshot) == "WIDEN_SPREAD_1_5X"
