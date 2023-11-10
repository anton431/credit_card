from decimal import Decimal

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.app.config.config import get_db
from src.app.config.database import POSTGRES_DB, POSTGRES_HOST, POSTGRES_PASSWORD, POSTGRES_PORT, POSTGRES_USER
from src.app.schemas.user import UpdateUser
from src.app.service import app

from src.app.data_sources.storages.log import LogStorage
from src.app.data_sources.storages.user import Transactions, UserStorage


SQLALCHEMY_DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
test_session=TestingSessionLocal()

def get_test_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = get_test_db

client = TestClient(app)

storage = UserStorage(session=test_session)
history = LogStorage(session=test_session)
transactions = Transactions(storage, history, session=test_session)

class Tests_Users(object):
    test_user_one = UpdateUser(card_number='100500', password='123123', limit=Decimal(1000), balance=Decimal(0), is_active=True)
    test_user_two = UpdateUser(card_number='139878', password='123123', limit=Decimal(1000), balance=Decimal(0), is_active=True)
