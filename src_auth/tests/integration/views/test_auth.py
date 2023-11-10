from decimal import Decimal
import os

from asgi_lifespan import LifespanManager
from fastapi.testclient import TestClient
from httpx import AsyncClient
import pytest

from src_auth.app.service import app
from src_auth.tests.utils import async_authentication_token_from_username, authentication_token_from_username


@pytest.mark.parametrize("card_number,password",
[
    pytest.param("100500", "123123", id="successful test get_balancen"),
]
)
def test_get_balancen(card_number, password):
    with TestClient(app) as client:
        headers = authentication_token_from_username(client, card_number, password)
        data_json = {"card_number": card_number}
        response = client.get("/api/balance", params=data_json, headers=headers)
    assert response.status_code == 200


@pytest.mark.parametrize("card_number, password, amount, expected",
[
    pytest.param("100500", "123123", Decimal(100), -100, id="successful test withdrawal"),
    pytest.param("100500", "123123", Decimal(500), -500, id="successful test withdrawal"),
]
)
def test_withdrawal(card_number, password, amount, expected):
    with TestClient(app) as client:
        headers = authentication_token_from_username(client, card_number, password)

        data_json = {"card_number": card_number}
        response = client.get("/api/balance", params=data_json, headers=headers)
        balance_before = int(response.json()['balance'])

        data_json = {"amount": amount, "card_number": card_number}
        response = client.post("/api/withdrawal", params=data_json, headers=headers)
        balance_after = int(response.json()['balance'])

        assert response.status_code == 200
        assert balance_after - balance_before ==  expected
        client.post("/api/deposit", params=data_json, headers=headers)


@pytest.mark.parametrize("card_number, password, amount, expected",
[
    pytest.param("100500", "123123", Decimal(100), 100, id="successful test deposit"),
    pytest.param("100500", "123123", Decimal(500), 500, id="successful test deposit"),
]
)
def test_deposit(card_number, password, amount, expected):
    with TestClient(app) as client:
        headers = authentication_token_from_username(client, card_number, password)

        data_json = {"card_number": card_number}
        response = client.get("/api/balance", params=data_json, headers=headers)
        balance_before = int(response.json()['balance'])

        data_json = {"amount": amount, "card_number": card_number}
        response = client.post("/api/deposit", params=data_json, headers=headers)
        balance_after = int(response.json()['balance'])

        assert response.status_code == 200
        assert balance_after - balance_before ==  expected
        client.post("/api/withdrawal", params=data_json, headers=headers)


def test_get_history():
    with TestClient(app) as client:
        headers = authentication_token_from_username(client, "100500", "123123")
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
                "year": 2023,
                "month": 10,
                "day": 1,
                "hour": 0,
                "minute": 0,
                "second": 0
            }
        }
        response = client.post("/api/balance/history?card_number=100500", json=data_json, headers=headers)
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_verify_endpoint():
    document = os.path.abspath(f'src_auth/img/document58815_test.jpg')
    selfie = os.path.abspath(f'src_auth/img/selfie58763_test.jpg')

    async with LifespanManager(app=app): 
        async with AsyncClient(app=app, base_url='http://test')  as client:
            headers = await async_authentication_token_from_username(client, "100500", "123123")
            response = await client.post(
                "/api/verify",
                files={
                    "selfie":  ("selfie58763_test.jpg", open(selfie, "rb"), "image/jpg"),
                    "document":  ("document58815_test.jpg", open(document, "rb"), "image/jpg"),
                },
                headers=headers
            )
    assert response.json() == {"card_number": "100500", "verified": "True", "status": "200"}


def test_get_metrics():
    with TestClient(app) as client:
        response = client.post("/metrics/")
    assert response.status_code == 200
    assert response