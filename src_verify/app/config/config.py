import os
from pydantic_settings import BaseSettings

HOST = os.getenv("HOST")
PORT_SRC = os.getenv("PORT_SRC")
KAFKA_HOST = os.getenv("KAFKA_HOST")
KAFKA_PORT = os.getenv("KAFKA_PORT")
SRC_HOST = os.getenv("SRC_HOST")

class Settings(BaseSettings):
    main_host: str = SRC_HOST #  src 0.0.0.0
    kafka:str = f'{KAFKA_HOST}:{KAFKA_PORT}' #  kafka:9092 localhost:24304

settings = Settings()
