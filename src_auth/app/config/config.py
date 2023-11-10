"""Settings auth."""
import os
from pydantic_settings import BaseSettings

from src_auth.app.config.database import SessionLocal
from src_auth.app.data_sources.storages.user import UserStorage

HOST = os.getenv("HOST")
PORT_SRC = os.getenv("PORT_SRC")
KAFKA_HOST = os.getenv("KAFKA_HOST")
KAFKA_PORT = os.getenv("KAFKA_PORT")
SRC_HOST = os.getenv("SRC_HOST")
SRC_VERIFY_HOST = os.getenv("SRC_VERIFY_HOST")
JAGER_HOST = os.getenv("JAGER_HOST")


class Settings(BaseSettings):
    main_host: str = SRC_HOST #  src 0.0.0.0
    verify_host: str = SRC_VERIFY_HOST #  src_verify 0.0.0.0
    kafka:str = f'{KAFKA_HOST}:{KAFKA_PORT}' #  kafka:9092 localhost:24304

settings = Settings()

session = SessionLocal()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 

storage = UserStorage(session=session)

SECRET_KEY = 'E80BCD4CA4ABE74AF4173EFCFD10C6BDAE7B449425E7AEC47D671345BFAA6D1Bc'  # noqa: E501
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30
