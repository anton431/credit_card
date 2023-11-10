import os
from aiohttp import ClientSession
from asgi_lifespan import LifespanManager

import pytest

from src_verify.app.views.verify import app, verify_point

@pytest.mark.asyncio
async def test_verify_point():
    document = os.path.abspath(f'src_verify/img/document58815_test.jpg')
    selfie = os.path.abspath(f'src_verify/img/selfie58763_test.jpg')

    async with LifespanManager(app): 
        async with ClientSession() as session:
            response = await verify_point(
                card_number='100500',
                selfie_path=selfie,
                document_path=document,
                session=session,
                kafka_producer=app.state.kafka_producer,
            )
    assert response == {'card_number': '100500', 'status': '200', 'verified': 'True'}