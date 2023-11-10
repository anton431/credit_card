"""Settings BD."""
import os

from src.app.config.database import SessionLocal
from src.app.data_sources.storages.log import LogStorage
from src.app.data_sources.storages.user import Transactions, UserStorage


HOST = os.getenv("HOST")
PORT_SRC = os.getenv("PORT_SRC")
JAGER_HOST = os.getenv("JAGER_HOST")


session=SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

storage = UserStorage(session=session)
history = LogStorage(session=session)
transactions = Transactions(storage, history, session=session)
