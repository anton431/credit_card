from decimal import Decimal
import pytest

from contextlib import nullcontext as does_not_raise
from src.app.models.user import User
from src.tests.conftest import Tests_Users, storage, transactions


@pytest.mark.parametrize("new_user,expected,expectation",
[
    pytest.param("100500", 1, pytest.raises(ValueError), id="card already exists"),
]
)
def test_UserStorage_add(new_user, expected, expectation):
    with expectation:
        storage.add(card_number=new_user, password=new_user)
        assert storage.get_user(new_user).id == expected

@pytest.mark.parametrize("card_number,expected,expectation",
[
    pytest.param("100500", User, does_not_raise(),id="successful get user"),
    pytest.param("139878", 1, pytest.raises(ValueError), id="card not exists"),
]
)
def test_UserStorage_get_user(card_number, expected, expectation):
    with expectation:
        assert type(storage.get_user(card_number)) == expected



@pytest.mark.parametrize("user,expected,expectation",
[
    pytest.param(Tests_Users.test_user_one, Decimal(1000), does_not_raise(), id="successful user update"),
    pytest.param(Tests_Users.test_user_two, Decimal(1000), pytest.raises(ValueError), id="user not exists"),
]
)
def test_UserStorage_update_user(user, expected, expectation):
    with expectation:
        storage.update_user(user)
        assert storage.get_user(user.card_number).limit == expected


@pytest.mark.parametrize("card_number,expected,expectation",
[
    pytest.param("100500", False, pytest.raises(ValueError), id="successful closed user"),
]
)
def test_UserStorage_close(card_number, expected, expectation):
    storage.close(card_number)
    with expectation:
        assert storage.get_user(card_number) == expected
    storage.update_user(Tests_Users.test_user_one)
    


@pytest.mark.parametrize("card_number,expected",
[
    pytest.param("100500", 0, id="successful get balance"),
]
)
def test_Transactions_get_balance(card_number, expected):
    assert transactions.get_balance(card_number) == expected


@pytest.mark.parametrize("card_number, amount, expected",
[
    pytest.param("100500", 300, -300, id="successful withdrawal"),
    pytest.param("100500", 1100 , 0, id="exceeded the limit"),
    pytest.param("100500", -200, 0, id="negative amount"),
]
)
def test_Transactions_withdrawal(card_number, amount, expected):
    transactions.withdrawal(card_number, amount)
    assert transactions.get_balance(card_number) == expected
    transactions._Transactions__change_balance(card_number, 0)

@pytest.mark.parametrize("card_number, amount, expected",
[
    pytest.param("100500", 300 , 300, id="successful deposit"),
    pytest.param("100500", 1100 , 1100, id="deposit not exceeded the limit"),
    pytest.param("100500", -200, 0, id="negative amount"),
]
)
def test_Transactions_deposit(card_number, amount, expected):
    transactions.deposit(card_number, amount)
    assert transactions.get_balance(card_number) == expected
    transactions._Transactions__change_balance(card_number, 0)



@pytest.mark.parametrize("card_number, new_limit, expected",
[
    pytest.param("100500", 2000, 2000, id="successful change limit"),
    pytest.param("100500", 3000, 3000, id="successful change limit"),
]
)
def test_Transactions_change_limit(card_number, new_limit, expected):
    transactions.change_limit(card_number, new_limit)
    assert storage.get_user(card_number).limit== expected
    