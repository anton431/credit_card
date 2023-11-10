"""API modul."""
from contextlib import asynccontextmanager
from datetime import datetime
from decimal import Decimal

from prometheus_client import make_asgi_app
from fastapi import Depends, FastAPI, responses, status
from sqlalchemy.orm import Session
from jaeger_client import Config
from starlette.middleware.base import BaseHTTPMiddleware

from src.app.config import config
from src.app.data_sources.storages.log import LogStorage
from src.app.data_sources.storages.user import Transactions, UserStorage
from src.app.middlewares import metrics_middleware, tracing_middleware
from src.app.models.user import Time
from src.app.schemas.log import HistoryLog
from src.app.schemas.user import User
from src.app.user import controller

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Инициализация глобального трейсера Jaeger
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
        service_name='adontsov-servic-src',
        validate=True,
    )
    tracer = conf.initialize_tracer()
    yield {'jaeger_tracer': tracer}


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


@app.get('/api/balance', response_model=User)
def get_balance(card_number: str, session: Session = Depends(config.get_db)):
    """Get balance."""
    user = controller.get_current_user(card_number, session)
    return User(
        card_number=card_number, balance=user._balance,
    )


@app.post('/api/change_limit')
def get_change_limit(
    card_number: str,
    new_limit: Decimal,
    session: Session = Depends(config.get_db),
):
    """Get balance."""
    storage = UserStorage(session)
    history = LogStorage(session)
    transactions = Transactions(storage, history, session)
    transactions.change_limit(
        card_number=card_number,
        new_limit=new_limit,
    )
    return {'new_limit': new_limit}


@app.post('/api/balance/history', response_model=list[HistoryLog])
def get_history(
    time_from: Time,
    time_to: Time,
    card_number: str,
    session: Session = Depends(config.get_db),
):
    """Get history balance."""
    history = LogStorage(session)
    history_tansactions = history.get_balance_history(
        card_number=card_number,
        time_from=datetime(
            year=time_from.year,
            month=time_from.month,
            day=time_from.day,
            hour=time_from.hour,
            minute=time_from.minute,
            second=time_from.second,
        ),
        time_to=datetime(
            year=time_to.year,
            month=time_to.month,
            day=time_to.day,
            hour=time_to.hour,
            minute=time_to.minute,
            second=time_to.second,
        ),
    )
    return [HistoryLog(
        card_number=log.card_number,
        after=log.after,
        before=log.before,
        changes=log.changes,
        datetime_utc=log._datetime_utc,
        user_id=log.user_id,
        )  # noqa: E123
        for log in history_tansactions
    ]


@app.post('/api/withdrawal', response_model=User)
def withdrawal(
    amount: Decimal,
    card_number: str,
    session: Session = Depends(config.get_db),
):
    """Withdrawal."""
    storage = UserStorage(session)
    history = LogStorage(session)
    transactions = Transactions(storage, history, session)
    transactions.withdrawal(card_number, amount)
    user = controller.get_current_user(card_number, session)
    return User(
        card_number=card_number, balance=user._balance,
    )


@app.post('/api/deposit', response_model=User)
def deposit(
    amount: Decimal,
    card_number: str,
    session: Session = Depends(config.get_db),
):
    """Deposit."""
    storage = UserStorage(session)
    history = LogStorage(session)
    transactions = Transactions(storage, history, session)
    transactions.deposit(card_number, amount)
    user = controller.get_current_user(card_number, session)
    return User(
        card_number=card_number, balance=user._balance,
    )

metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
app.add_middleware(BaseHTTPMiddleware, dispatch=metrics_middleware)
app.add_middleware(BaseHTTPMiddleware, dispatch=tracing_middleware)
