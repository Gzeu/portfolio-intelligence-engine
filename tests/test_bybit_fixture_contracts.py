import json
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures" / "bybit"
REQUIRED_ENVELOPE_KEYS = {"retCode", "retMsg", "result", "time"}


def all_fixture_files() -> list[Path]:
    return sorted(FIXTURES.glob("*.json"))


@pytest.mark.parametrize("fixture_path", all_fixture_files(), ids=lambda p: p.name)
def test_fixture_matches_bybit_v5_envelope(fixture_path: Path) -> None:
    payload = json.loads(fixture_path.read_text())
    assert REQUIRED_ENVELOPE_KEYS.issubset(payload.keys())
    assert payload["retCode"] == 0
    assert isinstance(payload["result"], dict)
    assert isinstance(payload["time"], int)


def test_all_expected_fixtures_exist() -> None:
    names = {path.name for path in all_fixture_files()}
    expected = {"system_status.json", "ticker_egldusdt.json", "instrument_egldusdt.json", "wallet_balance.json", "position_list.json", "orderbook_egldusdt.json"}
    assert expected.issubset(names)
