"""API modul."""
import datetime
import json
import os
from contextlib import asynccontextmanager
from decimal import Decimal
from typing import Annotated

import aiojobs
from aiohttp import ClientSession, TCPConnector
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer, ConsumerRecord
from opentracing import Format, global_tracer
from prometheus_client import Counter, Gauge, make_asgi_app
from fastapi import (Depends, FastAPI, File, HTTPException, Request,
                     UploadFile, responses, status)
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from jaeger_client import Config

from src_auth.app.middlewares import metrics_middleware, tracing_middleware, metrics_count_middleware
from src_auth.app.auth import controller
from src_auth.app.config import config
from src_auth.app.models.models import Time
from src_auth.app.schemas.auth import Token, User


@asynccontextmanager
async def lifespan(app: FastAPI):  # noqa: WPS217
    """lifespan."""
    session = ClientSession(connector=TCPConnector(verify_ssl=False), trust_env=True)  # noqa: DAR301
    conf = Config(
        config={
            'sampler': {
                'type': 'const',
                'param': 1,
            },
            'local_agent': {
                'reporting_host': config.JAGER_HOST,
                'reporting_port': 6831,
            },
            'logging': True,
        },
        service_name='adontsov-servic-src-auth',
        validate=True,
    )
    tracer = conf.initialize_tracer()
    scheduler = aiojobs.Scheduler()
    kafka_producer = AIOKafkaProducer(bootstrap_servers=config.settings.kafka)
    app.state.kafka_producer = kafka_producer
    app.state.client_session = session
    await kafka_producer.start()
    kafka_consumer = AIOKafkaConsumer(
        'verify_response', bootstrap_servers=config.settings.kafka,
    )
    app.state.kafka_consumer = kafka_consumer
    await kafka_consumer.start()
    yield {
        'client_session': session,
        'kafka_producer': kafka_producer,
        'kafka_consumer': kafka_consumer,
        'jaeger_tracer': tracer,
    }
    await kafka_consumer.stop()
    await scheduler.close()
    await session.close()
    await kafka_producer.stop()


is_live = True
app = FastAPI(lifespan=lifespan)

gauge_metric = Gauge('adontsov_ready_metric', 'Ready probe', ['endpoint'])

requests_num_success_verify = Counter(
    'adontsov_auth_verify_request_number',
    'Count number of success verify requests',
    ['endpoint', 'http_status_code', 'verified'],
)


@app.get('/ready')
def ready():
    gauge_metric.labels('/ready').set(1)
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


@app.post('/api/verify')
async def verify_endpoint(  # noqa: WPS210
    request: Request,
    current_user: Annotated[
        User,
        Depends(controller.get_current_user),
    ],
    selfie: UploadFile = File(...),
    document: UploadFile = File(...),
):
    """Verify photo endpoint."""
    with global_tracer().start_span('verify_endpoint') as span:
        selfiename = f'selfie{datetime.datetime.now().microsecond}.jpg'
        documentname = f'document{datetime.datetime.now().microsecond}.jpg'

        selfie_path = os.path.abspath(
            f'src_auth/img/{selfiename}',
        )
        document_path = os.path.abspath(
            f'src_auth/img/{documentname}',
        )

        with open(selfie_path, 'wb') as selfie_file:
            selfie_file.write(selfie.file.read())
        with open(document_path, 'wb') as document_file:
            document_file.write(document.file.read())

        selfie_path_verify=selfie_path.replace('src_auth','src_verify')
        document_path_verify=document_path.replace('src_auth','src_verify')

        session = request.app.state.client_session
        headers = {}
        global_tracer().inject(span, Format.HTTP_HEADERS, headers)

        async with session.post(
            f'http://{config.settings.verify_host}:24204/api/add_img',
            data={
                    "selfie":  open(selfie_path, "rb"),
                    "document":  open(document_path, "rb")
                },
            headers=headers,
        ) as response:
            data = await response.json()
            status = response.status

        os.remove(selfie_path)
        os.remove(document_path)

        producer: AIOKafkaProducer = request.app.state.kafka_producer
        event = {
            'card_number': current_user.card_number,
            'selfie_path': selfie_path_verify,
            'document_path': document_path_verify,
        }
        await producer.send(
            topic='verify', value=bytes(str(event), encoding='utf-8'),
        )

        consumer: AIOKafkaConsumer = request.app.state.kafka_consumer
        get_record: ConsumerRecord = await consumer.getone()

        response = json.loads(get_record.value.decode('utf-8').replace("'", '"'))
        requests_num_success_verify.labels('/api/verify', status, response['verified']).inc()
        return response


@app.post('/api/auth', response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
):
    """
    Get a custom token from the database.

    Args:
        - form_data (OAuth2PasswordRequestForm): The form data
            containing the username and password.

    Returns:
        - The access token and token type.
    """
    user = controller.authenticate_user(
        card_number=form_data.username,
        password=form_data.password,
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Incorrect username or password',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = datetime.timedelta(
        minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES,
    )
    access_token = controller.create_access_token(
        data_user={'sub': user.card_number},
        expires_delta=access_token_expires,
    )

    return Token(access_token=access_token, token_type='bearer')  # noqa: S106


@app.get('/api/balance/', response_model=User)
async def get_balance(
    request: Request,
    current_user: Annotated[
        User,
        Depends(controller.get_current_user),
    ],
):
    """Get balance."""
    with global_tracer().start_span('get_balance') as span:
        session = request.state.client_session
        headers = {}
        global_tracer().inject(span, Format.HTTP_HEADERS, headers)
        async with session.get(
            f'http://{config.settings.main_host}:24104/api/balance?card_number={current_user.card_number}',    # noqa: E501
            headers=headers,
        ) as response:
            data = await response.json()
            status = response.status
        balance = data.get('balance')
        if status == 404 or balance is None:
            raise HTTPException(status_code=status, detail='Card not found.')
        elif status != 200:
            raise HTTPException(status_code=status, detail='Something went wrong.')
        return data


@app.post('/api/balance/history')
async def get_history(
    request: Request,
    time_from: Time,
    time_to: Time,
    current_user: Annotated[
        User,
        Depends(controller.get_current_user),
    ],
):
    """Get history balance."""
    data_json = {
        'time_from': {
            'year': time_from.year,
            'month': time_from.month,
            'day': time_from.day,
            'hour': time_from.hour,
            'minute': time_from.minute,
            'second': time_from.second,
        },
        'time_to': {
            'year': time_to.year,
            'month': time_to.month,
            'day': time_to.day,
            'hour': time_to.hour,
            'minute': time_to.minute,
            'second': time_to.second,
        },
    }
    with global_tracer().start_span('get_history') as span:
        session = request.state.client_session
        headers = {}
        global_tracer().inject(span, Format.HTTP_HEADERS, headers)
        async with session.post(
            f'http://{config.settings.main_host}:24104/api/balance/history?card_number={current_user.card_number}',  # noqa: E501
            json=data_json,
            headers=headers,
        ) as response:
            data = await response.json()
            status = response.status
        if status != 200:
            raise HTTPException(status_code=status, detail='Something went wrong.')
        return data


@app.post('/api/withdrawal', response_model=User)
async def withdrawal(
    request: Request,
    amount: Decimal,
    current_user: Annotated[
        User,
        Depends(controller.get_current_user),
    ],
):
    """Withdrawal."""
    with global_tracer().start_span('withdrawal') as span:
        session = request.state.client_session
        headers = {}
        global_tracer().inject(span, Format.HTTP_HEADERS, headers)
        async with session.post(
            f'http://{config.settings.main_host}:24104/api/withdrawal?amount={amount}&card_number={current_user.card_number}',  # noqa: E501
            headers=headers,
        ) as response:
            data = await response.json()
            status = response.status
        if status != 200:
            raise HTTPException(status_code=status, detail='Something went wrong.')
        return data


@app.post('/api/deposit', response_model=User)
async def deposit(
    request: Request,
    amount: Decimal,
    current_user: Annotated[
        User,
        Depends(controller.get_current_user),
    ],
):
    """Deposit."""
    with global_tracer().start_span('deposit') as span:
        session = request.state.client_session
        headers = {}
        global_tracer().inject(span, Format.HTTP_HEADERS, headers)
        async with session.post(
            f'http://{config.settings.main_host}:24104/api/deposit?amount={amount}&card_number={current_user.card_number}',  # noqa: E501
            headers=headers,
        ) as response:
            data = await response.json()
            status = response.status
        if status != 200:
            raise HTTPException(status_code=status, detail='Something went wrong.')
        return data

metrics_app = make_asgi_app()  # Инициализация ASGI-сервера для передачи метрик
app.mount("/metrics", metrics_app)
app.add_middleware(BaseHTTPMiddleware, dispatch=metrics_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=metrics_count_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=tracing_middleware)
app.add_middleware(
        CORSMiddleware,
        allow_origins=['*'],
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )
