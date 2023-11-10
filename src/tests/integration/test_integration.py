from datetime import datetime
from decimal import Decimal

import pytest

from src.app.models import log
from src.tests.conftest import Tests_Users, storage, transactions, history
from src.tests.conftest import client


@pytest.mark.parametrize("card_number, amount, time_from, time_to, expected",
[
    pytest.param("100500", 300 , datetime(2020, 2, 1), datetime(2025, 5, 8), -300, id="successful test integration"),
]
)
def test_Deposit_Withdrawal_Get_balance_history(card_number, amount, time_from, time_to, expected):
    storage.update_user(Tests_Users.test_user_one)
    transactions._Transactions__drop_table(log.BalanceLog)
    transactions.deposit(card_number, amount)
    transactions.withdrawal(card_number, amount + 300)
    assert transactions.get_balance(card_number) == expected
    assert len(history.get_balance_history(card_number, time_from, time_to)) == 2
    transactions._Transactions__change_balance(card_number, Decimal(0))


@pytest.mark.parametrize("client,card_number",
[
    pytest.param(client, "100500", id="successful test get_balancen"),
]
)
def test_get_balancen(client, card_number):
    data_json = {"card_number": card_number}
    response = client.get("/api/balance", params=data_json)
    assert response.status_code == 200
    assert response.json() == {'balance': '0', 'card_number': '100500'}


@pytest.mark.parametrize("client,card_number, amount, expected",
[
    pytest.param(client, "100500", Decimal(100), '-100', id="successful test withdrawal"),
    pytest.param(client, "100500", Decimal(3100), '-100', id="successful test withdrawal"),
]
)
def test_withdrawal(client, card_number, amount, expected):
    data_json = {"amount": amount, "card_number": card_number}
    response = client.post("/api/withdrawal", params=data_json)
    assert response.status_code == 200
    assert response.json() == {'balance': expected, 'card_number': '100500'}



@pytest.mark.parametrize("client,card_number, amount, expected",
[
    pytest.param(client, "100500", Decimal(100), '0', id="successful test deposit"),
    pytest.param(client, "100500", Decimal(1100), '1100', id="successful test withdrawal"),
]
)
def test_deposit(client, card_number, amount, expected):
    data_json = {"amount": amount, "card_number": card_number}
    response = client.post("/api/deposit", params=data_json)
    assert response.status_code == 200
    assert response.json() == {'balance': expected, 'card_number': '100500'}


def test_get_history():
    data_json = {
        "time_from": {
            "year": 2023,
            "month": 1,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0
        },
        "time_to": {
            "year": 2025,
            "month": 10,
            "day": 1,
            "hour": 0,
            "minute": 0,
            "second": 0
        }
    }
    response = client.post("/api/balance/history?card_number=100500", json=data_json)
    assert response.status_code == 200
    assert len(response.json()) == 5
