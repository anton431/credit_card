"""DeepFace verify."""
import asyncio
import functools
import json
from concurrent.futures import ProcessPoolExecutor
from contextlib import asynccontextmanager
from io import BytesIO
import os

import aiojobs
import numpy as np
from aiohttp import ClientSession
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from deepface import DeepFace
from fastapi import FastAPI, File, UploadFile, responses, status
from PIL import Image

from src_verify.app.config import config

resources = {}


async def verify_users(session, kafka_producer):
    """Take users from the topic and checks their photos."""
    consumer: AIOKafkaConsumer = resources.get('kafka_consumer')
    while True:  # noqa: WPS457
        await asyncio.sleep(1)
        new_client = await consumer.getone()

        new_client = json.loads(
            new_client.value.decode('utf-8').replace("'", '"'),
        )
        credit_card = new_client.get('card_number')
        if credit_card:
            selfie_path = new_client.get('selfie_path')
            document_path = new_client.get('document_path')
            await verify_point(
                credit_card,
                selfie_path,
                document_path,
                session,
                kafka_producer,
            )


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: WPS213, WPS217
    """lifespan."""
    session = ClientSession()  # noqa: DAR301
    scheduler = aiojobs.Scheduler()
    kafka_producer = AIOKafkaProducer(bootstrap_servers=config.settings.kafka)
    app.state.kafka_producer = kafka_producer
    await kafka_producer.start()
    kafka_consumer = AIOKafkaConsumer(
        'verify', bootstrap_servers=config.settings.kafka,
    )
    await kafka_consumer.start()
    resources['kafka_consumer'] = kafka_consumer
    await scheduler.spawn(verify_users(session, kafka_producer))
    yield {'client_session': session, 'kafka_producer': kafka_producer}
    await kafka_consumer.stop()
    await scheduler.close()
    await kafka_producer.stop()
    resources.clear()
    await session.close()


is_live = True
app = FastAPI(lifespan=lifespan)


@app.get('/ready')
def ready():
    return responses.Response(status_code=status.HTTP_200_OK)


@app.get('/live')
def live():
    global is_live
    if is_live:
        return responses.Response(status_code=status.HTTP_200_OK)
    return responses.Response(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@app.get('/kill_live')
def kill_live():
    global is_live
    is_live = False
    return responses.Response(status_code=status.HTTP_200_OK)


@app.post('/api/add_img')
def add_photo_to_img(
    selfie: UploadFile = File(...),
    document: UploadFile = File(...),
):
    selfie_path = os.path.abspath(
        f'src_verify/img/{str(selfie.filename)}',
    )
    document_path = os.path.abspath(
        f'src_verify/img/{str(document.filename)}',
    )

    with open(selfie_path, 'wb') as selfie_file:
        selfie_file.write(selfie.file.read())
    with open(document_path, 'wb') as document_file:
        document_file.write(document.file.read())
    return {'status':'OK'}


def verify_faces(selfie, document):
    """Verify_photo."""
    verify_data = DeepFace.verify(selfie, document)
    return bool(verify_data['verified'])


async def verify_point(  # noqa: WPS210
    card_number: str,
    selfie_path: str,
    document_path: str,
    session: ClientSession,
    kafka_producer: AIOKafkaProducer,
):
    """Verify_endpoint."""
    with open(selfie_path, 'rb') as selfie:
        selfie_b = selfie.read()

    with open(document_path, 'rb') as document:
        document_b = document.read()

    selfie_b = np.array(Image.open(BytesIO(selfie_b)))
    document_b = np.array(Image.open(BytesIO(document_b)))

    loop = asyncio.get_event_loop()
    executor = ProcessPoolExecutor(max_workers=2)
    partial_func = functools.partial(verify_faces, selfie_b, document_b)
    verified = await loop.run_in_executor(executor, partial_func)

    if verified:
        credit_limit = 100_000
    else:
        credit_limit = 20_000

    async with session.post(
        f'http://{config.settings.main_host}:24104/api/change_limit?card_number={card_number}&new_limit={credit_limit}',    # noqa: E501
    ) as response:
        await response.json()
        status = response.status

    producer: AIOKafkaProducer = kafka_producer
    event = {
        'card_number': card_number,
        'verified': f'{verified}',
        'status': f'{status}',
    }

    await producer.send(
        topic='verify_response', value=bytes(str(event), encoding='utf-8'),
    )
    return event
