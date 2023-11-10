import time

from fastapi import Request, Response
from opentracing import (
    InvalidCarrierException,
    SpanContextCorruptedException,
    global_tracer,
    propagation,
    tags,
)
from prometheus_client import Histogram, Counter
from starlette.status import HTTP_400_BAD_REQUEST

request_latency_histogram = Histogram(
    'adontsov_auth_service_request_histogram',  # Название метрики
    'Request latency.',  # Документация метрики
    ['operation', 'http_status_code', 'error'],  # Лейблы
)

requests_num = Counter(
    'adontsov_auth_counter_request_number',
    'Count number of requests.',
    ['operation', 'http_status_code'],
)

async def metrics_count_middleware(request: Request, call_next):
    """Middleware для реализации количества запросов."""
    response: Response = await call_next(request)
    operation = f'{request.method} {request.url.path}'
    requests_num.labels(
        operation,
        response.status_code,
    ).inc()
    return response

async def metrics_middleware(request: Request, call_next):
    """Middleware для реализации логгирования времени выполнения запроса."""
    start_time = time.monotonic()
    response: Response = await call_next(request)
    operation = f'{request.method} {request.url.path}'
    request_latency_histogram.labels(
        operation,
        response.status_code,
        response.status_code >= HTTP_400_BAD_REQUEST,
    ).observe(
        time.monotonic() - start_time,
    )
    return response

async def tracing_middleware(request: Request, call_next):
    """Middleware для реализации трейсинга."""
    path = request.url.path
    if path.startswith('/up') or path.startswith('/ready') or path.startswith('/metrics/') or path.startswith('/live') or path.startswith('/kill_live'):
        return await call_next(request)
    try:
        span_ctx = global_tracer().extract(propagation.Format.HTTP_HEADERS, request.headers)
    except (InvalidCarrierException, SpanContextCorruptedException):
        span_ctx = None
    span_tags = {
        tags.SPAN_KIND: tags.SPAN_KIND_RPC_SERVER,
        tags.HTTP_METHOD: request.method,
        tags.HTTP_URL: request.url,
    }
    with global_tracer().start_active_span(
        str(request.url.path), child_of=span_ctx, tags=span_tags,
    ):
        return await call_next(request)
