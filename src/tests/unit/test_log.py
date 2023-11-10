from datetime import datetime
import pytest

from src.tests.conftest import history


@pytest.mark.parametrize("card_number,time_from,time_to, expected",
[
    pytest.param("100500", datetime(2020, 2, 1), datetime(2025, 5, 8), True, id="successful get history"),
    pytest.param("100500", datetime(2023, 2, 1), datetime(2023, 2, 1), False, id="empty get history"),
]
)
def test_LogStorage_get_balance_history(card_number, time_from, time_to, expected):
    assert bool(len(history.get_balance_history(card_number, time_from, time_to))) == expected