"""main modul."""
import uvicorn

from src_auth.app.config.config import HOST, PORT_SRC
from src_auth.app.views.auth import app

if __name__ == '__main__':
    uvicorn.run(
        app=app,
        host=HOST,  # noqa: S104
        port=PORT_SRC,
        http='h11',
        ssl_keyfile='localhost.key',
        ssl_certfile='localhost.crt',
    )  # noqa: WPS432
